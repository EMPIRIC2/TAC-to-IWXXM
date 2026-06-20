import { createClient } from "jsr:@supabase/supabase-js@2.49.8";
import * as kv from "./kv_store.tsx";
// SERVICE_ROLE client for database operations (bypasses RLS)
const supabase = createClient(Deno.env.get("SUPABASE_URL") ?? "", Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "");
// Convert IWXXM to JSON format for database storage
function iwxxmToJson(iwxxmContent, originalName) {
  // Parse basic IWXXM structure
  const lines = iwxxmContent.split('\n');
  const observations = [];
  // Extract observations from IWXXM
  let currentObs = null;
  for (const line of lines){
    if (line.includes('<MeteorologicalAerodromeObservation>')) {
      currentObs = {};
    } else if (line.includes('</MeteorologicalAerodromeObservation>') && currentObs) {
      observations.push(currentObs);
      currentObs = null;
    } else if (currentObs) {
      // Extract data from XML tags
      const stationMatch = line.match(/<station>(.*?)<\/station>/);
      const timeMatch = line.match(/<observationTime>(.*?)<\/observationTime>/);
      const timestampMatch = line.match(/<timestamp>(.*?)<\/timestamp>/);
      const contentMatch = line.match(/<content>(.*?)<\/content>/);
      if (stationMatch) currentObs.station = stationMatch[1];
      if (timeMatch) currentObs.observationTime = timeMatch[1];
      if (timestampMatch) currentObs.timestamp = timestampMatch[1];
      if (contentMatch) currentObs.rawMetar = contentMatch[1];
    }
  }
  return {
    fileName: originalName,
    format: 'IWXXM',
    observations,
    totalObservations: observations.length,
    processedAt: new Date().toISOString()
  };
}
// Upload to primary database
async function uploadToPrimary(file, options) {
  try {
    const recordId = `primary_${file.id}_${Date.now()}`;
    const record = {
      id: recordId,
      userId: file.userId,
      userEmail: file.userEmail,
      originalFileName: file.originalName,
      uploadedAt: new Date().toISOString(),
      format: options.format,
      ...options.includeOriginal && {
        originalContent: file.originalContent
      },
      ...options.format === 'iwxxm' || options.format === 'both' ? {
        iwxxmContent: file.convertedContent
      } : {},
      ...options.format === 'json' || options.format === 'both' ? {
        jsonContent: iwxxmToJson(file.convertedContent, file.originalName)
      } : {},
      metadata: options.metadata || {}
    };
    await kv.set(`db_primary:${recordId}`, record);
    console.log(`File uploaded to primary database: ${recordId}`);
    return {
      success: true,
      recordId,
      destination: 'primary'
    };
  } catch (error) {
    console.error('Error uploading to primary database:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error uploading to primary database'
    };
  }
}
// Upload to archive database
async function uploadToArchive(file, options) {
  try {
    const recordId = `archive_${file.id}_${Date.now()}`;
    const record = {
      id: recordId,
      userId: file.userId,
      userEmail: file.userEmail,
      originalFileName: file.originalName,
      archivedAt: new Date().toISOString(),
      format: options.format,
      ...options.includeOriginal && {
        originalContent: file.originalContent
      },
      ...options.format === 'iwxxm' || options.format === 'both' ? {
        iwxxmContent: file.convertedContent
      } : {},
      ...options.format === 'json' || options.format === 'both' ? {
        jsonContent: iwxxmToJson(file.convertedContent, file.originalName)
      } : {},
      metadata: {
        ...options.metadata,
        archiveVersion: '1.0'
      }
    };
    await kv.set(`db_archive:${recordId}`, record);
    console.log(`File uploaded to archive database: ${recordId}`);
    return {
      success: true,
      recordId,
      destination: 'archive'
    };
  } catch (error) {
    console.error('Error uploading to archive database:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error uploading to archive database'
    };
  }
}
// Main upload function
export async function uploadToDatabase(files, options) {
  const results = [];
  for (const file of files){
    if (options.destination === 'primary') {
      const result = await uploadToPrimary(file, options);
      results.push(result);
    } else if (options.destination === 'archive') {
      const result = await uploadToArchive(file, options);
      results.push(result);
    } else if (options.destination === 'both') {
      const primaryResult = await uploadToPrimary(file, options);
      const archiveResult = await uploadToArchive(file, options);
      results.push(primaryResult, archiveResult);
    }
  }
  const summary = {
    success: results.filter((r)=>r.success).length,
    failed: results.filter((r)=>!r.success).length
  };
  return {
    results,
    summary
  };
}
// Get uploaded files for a user
export async function getUserUploads(userId, database) {
  try {
    const allRecords = [];
    if (database === 'primary' || database === 'both') {
      const primaryRecords = await kv.getByPrefix(`db_primary:`);
      const userPrimaryRecords = primaryRecords.filter((record)=>record.userId === userId);
      allRecords.push(...userPrimaryRecords);
    }
    if (database === 'archive' || database === 'both') {
      const archiveRecords = await kv.getByPrefix(`db_archive:`);
      const userArchiveRecords = archiveRecords.filter((record)=>record.userId === userId);
      allRecords.push(...userArchiveRecords);
    }
    console.log(`Retrieved ${allRecords.length} uploads for user: ${userId}`);
    return {
      data: allRecords
    };
  } catch (error) {
    console.error('Error getting user uploads:', error);
    return {
      error: error instanceof Error ? error.message : 'Unknown error getting user uploads'
    };
  }
}
// Delete an upload
export async function deleteUpload(recordId, userId) {
  try {
    const record = await kv.get(`db_primary:${recordId}`) || await kv.get(`db_archive:${recordId}`);
    if (!record) {
      return {
        error: 'Record not found'
      };
    }
    if (record.userId !== userId) {
      return {
        error: 'Unauthorized: You can only delete your own uploads'
      };
    }
    if (await kv.get(`db_primary:${recordId}`)) {
      await kv.del(`db_primary:${recordId}`);
    } else {
      await kv.del(`db_archive:${recordId}`);
    }
    console.log(`Upload deleted: ${recordId} by user: ${userId}`);
    return {
      data: {
        message: 'Upload deleted successfully'
      }
    };
  } catch (error) {
    console.error('Error deleting upload:', error);
    return {
      error: error instanceof Error ? error.message : 'Unknown error deleting upload'
    };
  }
}
