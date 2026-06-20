import { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Card } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Upload, X, Download, Copy, FileText, Loader2, Database, Settings, ChevronDown, ChevronUp, Shield, LogOut, AlertCircle, XCircle } from 'lucide-react';
import JSZip from 'jszip';
import { toast } from 'sonner';
import { ThemeToggle } from './ThemeToggle';
import { DatabaseUploadDialog } from './DatabaseUploadDialog';
import { UserPreferencesDialog } from './UserPreferencesDialog';
import { IcaoAutocomplete } from './IcaoAutocomplete';
import { signOutWithScope } from '/utils/supabase/logout';
import { convertMetarToIwxxm as callBackendConversion } from '/utils/api';

interface ConvertedFile {
  id: string;
  originalName: string;
  originalContent: string;
  convertedContent: string;
  timestamp: number;
}

interface PendingFile {
  id: string;
  name: string;
  content: string;
}

interface FileConverterProps {
  onLogout: () => void;
  userEmail: string;
  accessToken?: string;
  onSwitchToAdmin?: () => void;
}

type IWXXMVersion = "2025-2" | "2023-1";
type OnErrorBehavior = "skip" | "fail" | "warn";
type LogLevel = "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL";

interface ConversionParams {
  bulletinId: string;
  issuingCenter: string;
  iwxxmVersion: IWXXMVersion;
  strictValidation: boolean;
  includeNilReasons: boolean;
  onError: OnErrorBehavior;
  logLevel: LogLevel;
}

export function FileConverter({ onLogout, userEmail, accessToken, onSwitchToAdmin }: FileConverterProps) {
  const [pendingFiles, setPendingFiles] = useState<PendingFile[]>([]);
  const [convertedFiles, setConvertedFiles] = useState<ConvertedFile[]>([]);
  const [manualInput, setManualInput] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [isConverting, setIsConverting] = useState(false);
  const [conversionStatus, setConversionStatus] = useState<{ type: 'idle' | 'loading' | 'timeout' | 'error'; message?: string }>({ type: 'idle' });
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
  const [isPreferencesDialogOpen, setIsPreferencesDialogOpen] = useState(false);
  const [isParamsExpanded, setIsParamsExpanded] = useState(false);
  const [isLogoutMenuOpen, setIsLogoutMenuOpen] = useState(false);
  const [conversionParams, setConversionParams] = useState<ConversionParams>({
    bulletinId: '',
    issuingCenter: '',
    iwxxmVersion: '2025-2',
    strictValidation: true,
    includeNilReasons: true,
    onError: 'warn',
    logLevel: 'INFO',
  });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleLogoutWithScope = async (scope: 'global' | 'local' | 'others') => {
    const success = await signOutWithScope(scope);
    if (success) {
      setIsLogoutMenuOpen(false);
      setTimeout(() => {
        onLogout();
      }, 500);
    }
  };

  // Load user preferences on mount from localStorage
  useEffect(() => {
    const loadPreferences = () => {
      try {
        const stored = localStorage.getItem('metar_converter_preferences');
        if (stored) {
          const prefs = JSON.parse(stored);
          // Migrate old version identifiers to new ones
          let iwxxmVersion: IWXXMVersion = '2025-2';
          if (prefs.iwxxmVersion === '2023-1') {
            iwxxmVersion = '2023-1';
          } else {
            // Default any other version (3.0, 2.1, 2021-2) to 2025-2
            iwxxmVersion = '2025-2';
          }
          
          setConversionParams({
            bulletinId: prefs.bulletinIdExample || 'SAAA00',
            issuingCenter: prefs.issuingCenter || 'KWBC',
            iwxxmVersion,
            strictValidation: prefs.strictValidation ?? true,
            includeNilReasons: prefs.includeNilReasons ?? true,
            onError: prefs.onError || 'warn',
            logLevel: prefs.logLevel || 'INFO',
          });
        }
      } catch (error) {
        console.error('Error loading preferences:', error);
      }
    };

    loadPreferences();
  }, []);

  const handlePreferencesSaved = () => {
    // Reload preferences after saving in the dialog
    try {
      const stored = localStorage.getItem('metar_converter_preferences');
      if (stored) {
        const prefs = JSON.parse(stored);
        // Migrate old version identifiers to new ones
        let iwxxmVersion: IWXXMVersion = '2025-2';
        if (prefs.iwxxmVersion === '2023-1') {
          iwxxmVersion = '2023-1';
        } else {
          // Default any other version (3.0, 2.1, 2021-2) to 2025-2
          iwxxmVersion = '2025-2';
        }
        
        setConversionParams({
          bulletinId: prefs.bulletinIdExample || 'SAAA00',
          issuingCenter: prefs.issuingCenter || 'KWBC',
          iwxxmVersion,
          strictValidation: prefs.strictValidation ?? true,
          includeNilReasons: prefs.includeNilReasons ?? true,
          onError: prefs.onError || 'warn',
          logLevel: prefs.logLevel || 'INFO',
        });
        toast.info('Conversion parameters updated from preferences');
      }
    } catch (error) {
      console.error('Error reloading preferences:', error);
    }
  };

  const handleFileSelect = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const newPendingFiles: PendingFile[] = [];
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      try {
        const content = await file.text();
        newPendingFiles.push({
          id: `${file.name}-${Date.now()}-${i}`,
          name: file.name,
          content: content,
        });
      } catch (error) {
        console.error(`Error reading file ${file.name}:`, error);
        toast.error(`Failed to read ${file.name}`);
      }
    }
    
    setPendingFiles(prev => [...prev, ...newPendingFiles]);
    toast.success(`${newPendingFiles.length} file(s) added to queue`);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleConvert = async () => {
    if (pendingFiles.length === 0 && !manualInput.trim()) {
      toast.error('Please add files or enter manual input');
      return;
    }

    setIsConverting(true);
    setConversionStatus({ type: 'loading', message: 'Converting...' });

    try {
      const newConvertedFiles: ConvertedFile[] = [];

      // Prepare files for conversion
      const filesToConvert: File[] = pendingFiles.map(file => {
        return new File([file.content], file.name, { type: 'text/plain' });
      });

      console.log('[FileConverter] Starting conversion with:', {
        manualInput: manualInput.trim() ? 'provided' : 'none',
        fileCount: filesToConvert.length,
        accessToken: accessToken ? `${accessToken.substring(0, 20)}...` : 'MISSING',
      });

      // Call backend API for conversion with timeout and token
      const response = await callBackendConversion({
        manualText: manualInput.trim() || undefined,
        files: filesToConvert.length > 0 ? filesToConvert : undefined,
        iwxxmVersion: conversionParams.iwxxmVersion,
        validateOutput: false,
        accessToken: accessToken,
      });

      console.log('[FileConverter] Conversion response:', response);

      // Process response and create converted file entries
      if (response.results && Array.isArray(response.results)) {
        response.results.forEach((result: { iwxxm_xml?: string; xml?: string; content?: string }, index: number) => {
          const originalFile = index < pendingFiles.length 
            ? pendingFiles[index]
            : { name: 'manual_input.txt', content: manualInput };
          
          newConvertedFiles.push({
            id: `converted-${Date.now()}-${index}`,
            originalName: originalFile.name,
            originalContent: originalFile.content,
            convertedContent: result.iwxxm_xml || result.xml || result.content || '',
            timestamp: Date.now(),
          });
        });
      }

      if (newConvertedFiles.length === 0) {
        toast.error('No files were converted');
        setConversionStatus({ type: 'error', message: 'No files were converted' });
        setIsConverting(false);
        return;
      }

      setConvertedFiles(prev => [...newConvertedFiles, ...prev]);
      setPendingFiles([]);
      setManualInput('');
      setConversionStatus({ type: 'idle' });
      toast.success(`Successfully converted ${newConvertedFiles.length} file(s)`);
    } catch (error) {
      console.error('[FileConverter] Conversion error:', error);
      
      const errorMessage = error instanceof Error ? error.message : 'Conversion failed. Please check the input and try again.';
      const isTimeout = errorMessage.includes('timeout') || errorMessage.includes('unreachable');
      const isAuthError = errorMessage.includes('401') || errorMessage.includes('unauthorized') || errorMessage.includes('Unauthorized');
      
      if (isTimeout) {
        const timeoutMsg = 'Conversion timeout - Backend may be unreachable. Please check if the API server is running.';
        setConversionStatus({ type: 'timeout', message: timeoutMsg });
        toast.error(timeoutMsg);
      } else if (isAuthError) {
        const authMsg = 'Authentication failed. Please ensure you are logged in.';
        setConversionStatus({ type: 'error', message: authMsg });
        toast.error(authMsg);
      } else {
        setConversionStatus({ type: 'error', message: errorMessage });
        toast.error(errorMessage);
      }
    } finally {
      setIsConverting(false);
    }
  };

  const handleDownloadSingle = (file: ConvertedFile) => {
    const blob = new Blob([file.convertedContent], { type: 'text/xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = file.originalName.replace(/\.(txt|metar)$/i, '.xml');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('File downloaded');
  };

  const handleDownloadAll = async () => {
    if (convertedFiles.length === 0) return;

    const zip = new JSZip();
    
    convertedFiles.forEach(file => {
      const filename = file.originalName.replace(/\.(txt|metar)$/i, '.xml');
      zip.file(filename, file.convertedContent);
    });

    const content = await zip.generateAsync({ type: 'blob' });
    const url = URL.createObjectURL(content);
    const a = document.createElement('a');
    a.href = url;
    a.download = `converted_files_${Date.now()}.zip`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('All files downloaded as ZIP');
  };

  const handleCopy = (content: string) => {
    // Try modern clipboard API first
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(content)
        .then(() => {
          toast.success('Copied to clipboard');
        })
        .catch(() => {
          // Fallback to older method
          fallbackCopy(content);
        });
    } else {
      // Fallback for browsers without clipboard API
      fallbackCopy(content);
    }
  };

  const fallbackCopy = (content: string) => {
    try {
      const textarea = document.createElement('textarea');
      textarea.value = content;
      textarea.style.position = 'fixed';
      textarea.style.left = '-9999px';
      textarea.style.top = '-9999px';
      document.body.appendChild(textarea);
      textarea.select();
      
      const successful = document.execCommand('copy');
      document.body.removeChild(textarea);
      
      if (successful) {
        toast.success('Copied to clipboard');
      } else {
        toast.error('Failed to copy. Please copy manually.');
      }
    } catch (err) {
      console.error('Copy failed:', err);
      toast.error('Failed to copy. Please copy manually.');
    }
  };

  const removePendingFile = (id: string) => {
    setPendingFiles(prev => prev.filter(f => f.id !== id));
  };

  const removeConvertedFile = (id: string) => {
    setConvertedFiles(prev => prev.filter(f => f.id !== id));
  };

  const handleClear = () => {
    setPendingFiles([]);
    setManualInput('');
    setConversionStatus({ type: 'idle' });
    toast.info('Queue cleared');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4 transition-colors">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-semibold text-gray-900 dark:text-white">METAR → IWXXM Converter</h1>
            <div className="flex items-center gap-3">
              {onSwitchToAdmin && (
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-purple-600 dark:text-purple-400" aria-hidden="true" />
                  <select
                    value="converter"
                    onChange={(e) => {
                      if (e.target.value === 'admin') {
                        console.log('User selected admin view from dropdown');
                        onSwitchToAdmin?.();
                      }
                    }}
                    className="px-3 py-1.5 text-sm font-medium bg-purple-600 text-white border-0 rounded-md hover:bg-purple-700 dark:bg-purple-700 dark:hover:bg-purple-800 focus:ring-2 focus:ring-purple-500 focus:outline-none cursor-pointer"
                    aria-label="Switch view"
                  >
                    <option value="converter" className="bg-white text-gray-900 dark:bg-gray-800 dark:text-white">File Converter</option>
                    <option value="admin" className="bg-white text-gray-900 dark:bg-gray-800 dark:text-white">Admin Dashboard</option>
                  </select>
                </div>
              )}
              <Button
                onClick={() => setIsPreferencesDialogOpen(true)}
                variant="outline"
                size="sm"
                className="dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600 focus:ring-2 focus:ring-gray-500"
                aria-label="Open user preferences"
              >
                <Settings className="w-4 h-4 mr-2" aria-hidden="true" />
                Preferences
              </Button>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">Theme</span>
                <ThemeToggle />
              </div>
              
              {/* Logout Menu */}
              <div className="relative">
                <Button 
                  variant="outline" 
                  className="bg-red-500 text-white hover:bg-red-600 dark:bg-red-600 dark:hover:bg-red-700 border-0"
                  aria-label="Logout options"
                  onClick={() => setIsLogoutMenuOpen(!isLogoutMenuOpen)}
                >
                  <LogOut className="w-4 h-4 mr-2" aria-hidden="true" />
                  Logout
                  <ChevronDown className="w-4 h-4 ml-1" aria-hidden="true" />
                </Button>
                
                {isLogoutMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg z-10">
                    <div className="p-3 space-y-2">
                      <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 px-2 py-1">Sign out scope:</p>
                      
                      <button
                        onClick={() => handleLogoutWithScope('local')}
                        className="w-full text-left px-3 py-2 rounded-md text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        aria-label="Sign out from this device only"
                      >
                        <div className="font-medium">This Device</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">Only this session</div>
                      </button>
                      
                      <button
                        onClick={() => handleLogoutWithScope('global')}
                        className="w-full text-left px-3 py-2 rounded-md text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        aria-label="Sign out from all devices"
                      >
                        <div className="font-medium">All Devices</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">Every logged-in session</div>
                      </button>
                      
                      <button
                        onClick={() => handleLogoutWithScope('others')}
                        className="w-full text-left px-3 py-2 rounded-md text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        aria-label="Sign out from other devices"
                      >
                        <div className="font-medium">Other Devices</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">Keep this session active</div>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
          <p className="text-base text-gray-600 dark:text-gray-300">
            Drag & drop one or more METAR TAC files, or type a METAR manually below. Click Convert to produce IWXXM XML (downloadable as XML).
          </p>
        </div>

        {/* Drop Zone */}
        <Card
          className={`mb-6 p-12 border-2 border-dashed transition-colors ${
            isDragging 
              ? 'border-blue-500 bg-blue-50 dark:border-blue-400 dark:bg-blue-950' 
              : 'border-gray-300 bg-white dark:border-gray-700 dark:bg-gray-800'
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          role="button"
          aria-label="File drop zone - Drop files here or click to select files"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              fileInputRef.current?.click();
            }
          }}
        >
          <div className="flex flex-col items-center justify-center text-center">
            <Upload className="w-12 h-12 text-gray-400 dark:text-gray-500 mb-4" aria-hidden="true" />
            <p className="text-lg mb-2 text-gray-900 dark:text-white">Drop files here or click to select</p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">Supports multiple files</p>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".txt,.metar"
              className="hidden"
              onChange={(e) => handleFileSelect(e.target.files)}
              aria-label="Select METAR files to upload"
            />
            <Button
              variant="outline"
              onClick={() => fileInputRef.current?.click()}
              className="dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              aria-label="Browse and select files"
            >
              Select Files
            </Button>
          </div>
        </Card>

        {/* Manual Input */}
        <div className="mb-6">
          <label htmlFor="manual-input" className="block mb-2 text-base font-medium text-gray-900 dark:text-white">
            Manual METAR Input
          </label>
          <Textarea
            id="manual-input"
            value={manualInput}
            onChange={(e) => setManualInput(e.target.value)}
            placeholder="SPECI BGSF 282350Z 10RMF50MT 9999 SCT110 BKN130 0RN130 NN7/N11 Q1021"
            className="min-h-[120px] text-sm dark:bg-gray-800 dark:text-white dark:border-gray-700 focus:ring-2 focus:ring-blue-500"
            aria-label="Enter METAR data manually"
          />
        </div>

        {/* Conversion Parameters */}
        <Card className="mb-6 p-6 bg-white dark:bg-gray-800 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Conversion Parameters</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsParamsExpanded(!isParamsExpanded)}
              className="hover:bg-gray-100 dark:hover:bg-gray-700 focus:ring-2 focus:ring-gray-500"
              aria-label={isParamsExpanded ? 'Collapse parameters' : 'Expand parameters'}
            >
              {isParamsExpanded ? (
                <ChevronUp className="w-4 h-4 text-gray-600 dark:text-gray-400" aria-hidden="true" />
              ) : (
                <ChevronDown className="w-4 h-4 text-gray-600 dark:text-gray-400" aria-hidden="true" />
              )}
            </Button>
          </div>
          <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 ${isParamsExpanded ? '' : 'hidden'}`}>
            {/* Bulletin ID */}
            <div>
              <Label htmlFor="param-bulletin-id" className="dark:text-white mb-2">Bulletin ID</Label>
              <Input
                id="param-bulletin-id"
                value={conversionParams.bulletinId}
                onChange={(e) => setConversionParams(prev => ({ ...prev, bulletinId: e.target.value.toUpperCase() }))}
                placeholder="SAAA00"
                maxLength={6}
                className="dark:bg-gray-700 dark:text-white dark:border-gray-600"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Format: 4 letters + 2 digits
              </p>
            </div>

            {/* Issuing Center */}
            <IcaoAutocomplete
              label="Issuing Center (ICAO)"
              id="param-issuing-center"
              value={conversionParams.issuingCenter}
              onChange={(value) => setConversionParams(prev => ({ ...prev, issuingCenter: value }))}
              placeholder="KWBC"
              maxLength={4}
              helperText="4-letter ICAO code"
            />

            {/* IWXXM Version */}
            <div>
              <Label htmlFor="param-iwxxm-version" className="dark:text-white mb-2">IWXXM Version</Label>
              <select
                id="param-iwxxm-version"
                value={conversionParams.iwxxmVersion}
                onChange={(e) => setConversionParams(prev => ({ ...prev, iwxxmVersion: e.target.value as IWXXMVersion }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
              >
                <option value="2025-2">2025-2 (Latest)</option>
                <option value="2023-1">2023-1 (Previous)</option>
              </select>
            </div>

            {/* On Error */}
            <div>
              <Label htmlFor="param-on-error" className="dark:text-white mb-2">On Error Behavior</Label>
              <select
                id="param-on-error"
                value={conversionParams.onError}
                onChange={(e) => setConversionParams(prev => ({ ...prev, onError: e.target.value as OnErrorBehavior }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
              >
                <option value="skip">Skip - Continue, skip invalid</option>
                <option value="fail">Fail - Stop on first error</option>
                <option value="warn">Warn - Continue with warnings</option>
              </select>
            </div>

            {/* Log Level */}
            <div>
              <Label htmlFor="param-log-level" className="dark:text-white mb-2">Log Level</Label>
              <select
                id="param-log-level"
                value={conversionParams.logLevel}
                onChange={(e) => setConversionParams(prev => ({ ...prev, logLevel: e.target.value as LogLevel }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
              >
                <option value="DEBUG">DEBUG</option>
                <option value="INFO">INFO (Default)</option>
                <option value="WARNING">WARNING</option>
                <option value="ERROR">ERROR</option>
                <option value="CRITICAL">CRITICAL</option>
              </select>
            </div>

            {/* Validation Options */}
            <div className="flex flex-col gap-3">
              <Label className="dark:text-white">Validation Options</Label>
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={conversionParams.strictValidation}
                  onChange={(e) => setConversionParams(prev => ({ ...prev, strictValidation: e.target.checked }))}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                  Strict Validation
                </span>
              </label>
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={conversionParams.includeNilReasons}
                  onChange={(e) => setConversionParams(prev => ({ ...prev, includeNilReasons: e.target.checked }))}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                  Include Nil Reasons
                </span>
              </label>
            </div>
          </div>
        </Card>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-3 mb-8 bg-[rgba(0,0,0,0)]">
          <Button
            onClick={handleConvert}
            disabled={isConverting || (pendingFiles.length === 0 && !manualInput.trim())}
            className="bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white text-base disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            aria-label={isConverting ? 'Converting files, please wait' : 'Convert METAR files to IWXXM XML'}
          >
            {isConverting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
                Converting...
              </>
            ) : (
              'Convert'
            )}
          </Button>
          <Button
            onClick={() => setIsUploadDialogOpen(true)}
            disabled={convertedFiles.length === 0}
            variant="outline"
            className="bg-green-600 text-white hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-800 text-base disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            aria-label={`Upload ${convertedFiles.length} converted files to database`}
          >
            <Database className="w-4 h-4 mr-2" aria-hidden="true" />
            Upload to Database {convertedFiles.length > 0 && `(${convertedFiles.length})`}
          </Button>
          <Button
            onClick={handleDownloadAll}
            disabled={convertedFiles.length === 0}
            variant="outline"
            className="bg-gray-600 text-white hover:bg-gray-700 dark:bg-gray-700 dark:hover:bg-gray-600 text-base disabled:opacity-50 disabled:cursor-not-allowed focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            aria-label={`Download all ${convertedFiles.length} converted files as ZIP`}
          >
            Download ZIP {convertedFiles.length > 0 && `(${convertedFiles.length})`}
          </Button>
          <Button
            onClick={handleClear}
            variant="outline"
            className="bg-gray-600 text-white hover:bg-gray-700 dark:bg-gray-700 dark:hover:bg-gray-600 text-base focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            aria-label="Clear all pending files and manual input"
          >
            Clear
          </Button>
        </div>

        {/* Conversion Status Display */}
        {conversionStatus.type !== 'idle' && (
          <div className={`mb-8 p-4 rounded-lg border-2 flex items-start gap-3 ${
            conversionStatus.type === 'loading' 
              ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-700' 
              : conversionStatus.type === 'timeout'
              ? 'bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-700'
              : 'bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-700'
          }`}>
            <div className="pt-1">
              {conversionStatus.type === 'loading' ? (
                <Loader2 className="w-5 h-5 text-blue-600 dark:text-blue-400 animate-spin flex-shrink-0" aria-hidden="true" />
              ) : conversionStatus.type === 'timeout' ? (
                <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0" aria-hidden="true" />
              ) : (
                <XCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0" aria-hidden="true" />
              )}
            </div>
            <div className="flex-1">
              <p className={`font-semibold ${
                conversionStatus.type === 'loading'
                  ? 'text-blue-900 dark:text-blue-100'
                  : 'text-red-900 dark:text-red-100'
              }`}>
                {conversionStatus.type === 'loading' ? 'Converting...' : 'Conversion Error'}
              </p>
              {conversionStatus.message && (
                <p className={`text-sm mt-1 ${
                  conversionStatus.type === 'loading'
                    ? 'text-blue-800 dark:text-blue-200'
                    : 'text-red-800 dark:text-red-200'
                }`}>
                  {conversionStatus.message}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Pending Files */}
        {pendingFiles.length > 0 && (
          <div className="mb-8" role="region" aria-label="Pending files queue">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Pending Files</h2>
            <div className="space-y-2">
              {pendingFiles.map((file) => (
                <Card key={file.id} className="p-4 bg-white dark:bg-gray-800 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <FileText className="w-5 h-5 text-blue-500 dark:text-blue-400" aria-hidden="true" />
                      <div>
                        <p className="text-base font-medium text-gray-900 dark:text-white">{file.name}</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {file.content.split('\n').length} line(s)
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removePendingFile(file.id)}
                      className="hover:bg-gray-100 dark:hover:bg-gray-700 focus:ring-2 focus:ring-red-500"
                      aria-label={`Remove ${file.name} from queue`}
                    >
                      <X className="w-4 h-4 text-gray-600 dark:text-gray-400" aria-hidden="true" />
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Results */}
        {convertedFiles.length > 0 && (
          <div role="region" aria-label="Conversion results">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Results</h2>
            <div className="space-y-4">
              {convertedFiles.map((file) => (
                <Card key={file.id} className="p-4 bg-white dark:bg-gray-800 dark:border-gray-700">
                  <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
                    <p className="text-base font-medium text-gray-900 dark:text-white">{file.originalName}</p>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDownloadSingle(file)}
                        className="bg-blue-500 text-white hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-sm border-0 focus:ring-2 focus:ring-blue-500"
                        aria-label={`Download ${file.originalName} as XML`}
                      >
                        <Download className="w-4 h-4 mr-1" aria-hidden="true" />
                        Download
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleCopy(file.convertedContent)}
                        className="bg-blue-500 text-white hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-sm border-0 focus:ring-2 focus:ring-blue-500"
                        aria-label={`Copy ${file.originalName} content to clipboard`}
                      >
                        <Copy className="w-4 h-4 mr-1" aria-hidden="true" />
                        Copy
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeConvertedFile(file.id)}
                        className="hover:bg-gray-100 dark:hover:bg-gray-700 focus:ring-2 focus:ring-red-500"
                        aria-label={`Remove ${file.originalName} from results`}
                      >
                        <X className="w-4 h-4 text-gray-600 dark:text-gray-400" aria-hidden="true" />
                      </Button>
                    </div>
                  </div>
                  <div 
                    className="bg-gray-900 dark:bg-gray-950 text-green-400 dark:text-green-300 p-4 rounded text-sm overflow-x-auto"
                    role="region"
                    aria-label={`Converted XML content for ${file.originalName}`}
                  >
                    <pre className="whitespace-pre-wrap break-all font-mono">
                      {file.convertedContent}
                    </pre>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-12 text-center text-sm text-gray-500 dark:text-gray-400">
          <p>
            Conversion powered by GIFS library Outputs.java raw IWXXM XML serialized to .txt for convenience.
          </p>
        </div>
      </div>

      {/* Database Upload Dialog */}
      <DatabaseUploadDialog
        convertedFiles={convertedFiles}
        isOpen={isUploadDialogOpen}
        onClose={() => setIsUploadDialogOpen(false)}
        accessToken={accessToken}
      />

      {/* User Preferences Dialog */}
      <UserPreferencesDialog
        isOpen={isPreferencesDialogOpen}
        onClose={() => setIsPreferencesDialogOpen(false)}
        userEmail={userEmail}
        onPreferencesSaved={handlePreferencesSaved}
      />
    </div>
  );
}