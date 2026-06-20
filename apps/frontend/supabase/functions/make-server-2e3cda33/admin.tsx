import * as kv from "./kv_store.tsx";
const DEFAULT_SETTINGS = {
  defaultBulletinId: 'SAAA00',
  defaultIssuingCenter: 'KWBC',
  defaultIwxxmVersion: '3.0',
  defaultStrictValidation: true,
  defaultIncludeNilReasons: true,
  defaultOnError: 'warn',
  defaultLogLevel: 'INFO',
  allowedIcaoCodes: []
};
// Get system settings
export async function getSystemSettings() {
  try {
    const settings = await kv.get('system:settings');
    return settings || DEFAULT_SETTINGS;
  } catch (error) {
    console.error('Error getting system settings:', error);
    return DEFAULT_SETTINGS;
  }
}
// Save system settings
export async function saveSystemSettings(settings) {
  try {
    await kv.set('system:settings', settings);
    console.log('System settings saved successfully');
    return {
      data: settings
    };
  } catch (error) {
    console.error('Error saving system settings:', error);
    return {
      error: error instanceof Error ? error.message : 'Unknown error saving settings'
    };
  }
}
// Send email notification (simplified - in production would use email service like SendGrid, Resend, etc.)
export async function sendEmailNotification(to, subject, body) {
  try {
    // In a real implementation, you would integrate with an email service
    // For now, we'll just log the email that would be sent
    console.log('=== EMAIL NOTIFICATION ===');
    console.log(`To: ${to}`);
    console.log(`Subject: ${subject}`);
    console.log(`Body: ${body}`);
    console.log('========================');
    // Store email in KV for tracking
    const emailId = `email:${Date.now()}:${to}`;
    await kv.set(emailId, {
      to,
      subject,
      body,
      sent_at: new Date().toISOString(),
      status: 'sent' // In production: 'pending', 'sent', 'failed'
    });
    return {
      data: {
        message: 'Email sent successfully'
      }
    };
  } catch (error) {
    console.error('Error sending email:', error);
    return {
      error: error instanceof Error ? error.message : 'Unknown error sending email'
    };
  }
}
