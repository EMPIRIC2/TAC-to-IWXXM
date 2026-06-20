import { useState } from 'react';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Card } from './ui/card';
import { Database, Upload, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { projectId } from '/utils/supabase/info';

interface DatabaseUploadDialogProps {
  convertedFiles: Array<{
    id: string;
    originalName: string;
    originalContent: string;
    convertedContent: string;
    timestamp: number;
  }>;
  isOpen: boolean;
  onClose: () => void;
  accessToken?: string;
}

type DatabaseFormat = 'iwxxm' | 'json' | 'both';
type UploadDestination = 'primary' | 'archive' | 'both';

export function DatabaseUploadDialog({ 
  convertedFiles, 
  isOpen, 
  onClose,
  accessToken 
}: DatabaseUploadDialogProps) {
  const [format, setFormat] = useState<DatabaseFormat>('iwxxm');
  const [destination, setDestination] = useState<UploadDestination>('primary');
  const [includeOriginal, setIncludeOriginal] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');

  if (!isOpen) return null;

  const handleUpload = async () => {
    if (!accessToken) {
      toast.error('Authentication required. Please log in again.');
      return;
    }

    setIsUploading(true);
    setUploadStatus('idle');

    try {
      const response = await fetch(
        `https://${projectId}.supabase.co/functions/v1/make-server-2e3cda33/database/upload`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`,
          },
          body: JSON.stringify({
            files: convertedFiles,
            options: {
              format,
              destination,
              includeOriginal,
            },
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to upload to database');
      }

      setUploadStatus('success');
      toast.success(data.message || 'Files uploaded successfully');
      
      // Auto-close after success
      setTimeout(() => {
        onClose();
        setUploadStatus('idle');
      }, 2000);
    } catch (error) {
      console.error('Database upload error:', error);
      setUploadStatus('error');
      toast.error(error instanceof Error ? error.message : 'Failed to upload to database');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="upload-dialog-title"
    >
      <Card 
        className="bg-white dark:bg-gray-800 dark:border-gray-700 p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <Database className="w-6 h-6 text-blue-500 dark:text-blue-400" aria-hidden="true" />
          <h2 id="upload-dialog-title" className="text-2xl font-semibold text-gray-900 dark:text-white">
            Upload to Database
          </h2>
        </div>

        {/* Info */}
        <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg">
          <p className="text-sm text-gray-700 dark:text-gray-300">
            Uploading <strong>{convertedFiles.length}</strong> converted file(s) to database
          </p>
        </div>

        {/* Format Selection */}
        <div className="mb-6">
          <Label className="text-base font-medium mb-3 block dark:text-white">
            Storage Format
          </Label>
          <div className="space-y-2">
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="format"
                value="iwxxm"
                checked={format === 'iwxxm'}
                onChange={(e) => setFormat(e.target.value as DatabaseFormat)}
                className="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
                aria-label="Store as IWXXM XML only"
              />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                <strong>IWXXM XML</strong> - Store converted XML format only
              </span>
            </label>
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="format"
                value="json"
                checked={format === 'json'}
                onChange={(e) => setFormat(e.target.value as DatabaseFormat)}
                className="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
                aria-label="Store as parsed JSON only"
              />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                <strong>JSON</strong> - Store parsed JSON representation
              </span>
            </label>
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="format"
                value="both"
                checked={format === 'both'}
                onChange={(e) => setFormat(e.target.value as DatabaseFormat)}
                className="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
                aria-label="Store both IWXXM XML and JSON formats"
              />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                <strong>Both</strong> - Store both XML and JSON formats
              </span>
            </label>
          </div>
        </div>

        {/* Destination Selection */}
        <div className="mb-6">
          <Label className="text-base font-medium mb-3 block dark:text-white">
            Destination Database
          </Label>
          <div className="space-y-2">
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="destination"
                value="primary"
                checked={destination === 'primary'}
                onChange={(e) => setDestination(e.target.value as UploadDestination)}
                className="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
                aria-label="Upload to primary database"
              />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                <strong>Primary Database</strong> - Active operational database
              </span>
            </label>
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="destination"
                value="archive"
                checked={destination === 'archive'}
                onChange={(e) => setDestination(e.target.value as UploadDestination)}
                className="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
                aria-label="Upload to archive database"
              />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                <strong>Archive Database</strong> - Long-term storage and historical records
              </span>
            </label>
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="destination"
                value="both"
                checked={destination === 'both'}
                onChange={(e) => setDestination(e.target.value as UploadDestination)}
                className="w-4 h-4 text-blue-600 focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
                aria-label="Upload to both primary and archive databases"
              />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                <strong>Both Databases</strong> - Upload to both primary and archive
              </span>
            </label>
          </div>
        </div>

        {/* Additional Options */}
        <div className="mb-6">
          <Label className="text-base font-medium mb-3 block dark:text-white">
            Additional Options
          </Label>
          <label className="flex items-start cursor-pointer">
            <input
              type="checkbox"
              checked={includeOriginal}
              onChange={(e) => setIncludeOriginal(e.target.checked)}
              className="w-4 h-4 mt-0.5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700"
              aria-label="Include original METAR content in upload"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              <strong>Include Original METAR</strong> - Store the original METAR content alongside converted data
            </span>
          </label>
        </div>

        {/* Status Messages */}
        {uploadStatus === 'success' && (
          <div className="mb-6 p-4 bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-lg flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0" aria-hidden="true" />
            <p className="text-sm text-green-700 dark:text-green-300">
              Files uploaded successfully!
            </p>
          </div>
        )}

        {uploadStatus === 'error' && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0" aria-hidden="true" />
            <p className="text-sm text-red-700 dark:text-red-300">
              Upload failed. Please try again.
            </p>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3 justify-end">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isUploading}
            className="dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600 focus:ring-2 focus:ring-gray-500"
            aria-label="Cancel database upload"
          >
            Cancel
          </Button>
          <Button
            onClick={handleUpload}
            disabled={isUploading}
            className="bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label={isUploading ? 'Uploading to database, please wait' : 'Upload files to database'}
          >
            {isUploading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4 mr-2" aria-hidden="true" />
                Upload to Database
              </>
            )}
          </Button>
        </div>
      </Card>
    </div>
  );
}
