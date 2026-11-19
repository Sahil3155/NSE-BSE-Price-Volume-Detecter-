import React, { useEffect, useState, useRef } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import { fetchMarketDataStatus, uploadDatasetFile, MarketDataStatus, UploadResult } from '../services/dataService';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const DataManagement: React.FC = () => {
  const [status, setStatus] = useState<MarketDataStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [exchange, setExchange] = useState('NSE');
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const loadStatus = () => {
    setLoading(true);
    fetchMarketDataStatus()
      .then(setStatus)
      .catch((err) => console.error('Status fetch error:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setErrorMsg(null);
    setUploadResult(null);

    try {
      const result = await uploadDatasetFile(file, exchange);
      setUploadResult(result);
      loadStatus();
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'File ingestion failed. Check CSV schema.');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-100">Market Data Pipeline & Ingestion</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Import official NSE/BSE Bhavcopy CSV or ZIP archives with duplicate suppression.
          </p>
        </div>
      </div>

      {/* Dataset Status Summary */}
      {loading ? (
        <LoadingSpinner message="Checking dataset coverage..." />
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-surface border border-border rounded-lg p-4">
            <p className="text-xs text-gray-400 uppercase">Equities Registered</p>
            <p className="text-2xl font-bold text-gray-100 mt-1">{status?.total_stocks || 0}</p>
            <p className="text-xs text-gray-400 mt-1">Unique ticker symbols</p>
          </div>

          <div className="bg-surface border border-border rounded-lg p-4">
            <p className="text-xs text-gray-400 uppercase">Historical Sessions</p>
            <p className="text-2xl font-bold text-cyan-400 mt-1">{status?.total_market_records || 0}</p>
            <p className="text-xs text-gray-400 mt-1">OHLCV records stored</p>
          </div>

          <div className="bg-surface border border-border rounded-lg p-4">
            <p className="text-xs text-gray-400 uppercase">Feature Vectors</p>
            <p className="text-2xl font-bold text-accent mt-1">{status?.total_featured_records || 0}</p>
            <p className="text-xs text-gray-400 mt-1">Engineered surveillance vectors</p>
          </div>

          <div className="bg-surface border border-border rounded-lg p-4">
            <p className="text-xs text-gray-400 uppercase">Date Coverage</p>
            <p className="text-sm font-semibold text-gray-200 mt-1">
              {status?.earliest_trading_date || 'N/A'} to {status?.latest_trading_date || 'N/A'}
            </p>
            <p className="text-xs text-gray-400 mt-1">Exchanges: {status?.exchanges.join(', ') || 'None'}</p>
          </div>
        </div>
      )}

      {/* Upload Box */}
      <div className="bg-surface border border-border rounded-lg p-6 space-y-4">
        <h3 className="text-sm font-semibold text-gray-200 flex items-center space-x-2">
          <Upload className="w-4 h-4 text-accent" />
          <span>Ingest Bhavcopy / Market Dataset</span>
        </h3>

        <div className="flex items-center space-x-4">
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">Exchange Source</label>
            <select
              value={exchange}
              onChange={(e) => setExchange(e.target.value)}
              className="bg-background border border-border rounded-md px-3 py-2 text-xs text-gray-100"
            >
              <option value="NSE">National Stock Exchange (NSE Bhavcopy)</option>
              <option value="BSE">Bombay Stock Exchange (BSE Bhavcopy)</option>
            </select>
          </div>
        </div>

        <div className="border-2 border-dashed border-border rounded-lg p-8 text-center flex flex-col items-center justify-center hover:border-accent/60 transition-colors">
          <FileText className="w-10 h-10 text-gray-400 mb-3" />
          <p className="text-sm text-gray-200 font-medium">Click or drag & drop CSV or ZIP Bhavcopy file</p>
          <p className="text-xs text-gray-400 mt-1 max-w-sm">
            Supports legacy NSE/BSE schemas and UDiFF formats. Duplicates are suppressed automatically.
          </p>

          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.zip"
            onChange={handleFileChange}
            disabled={uploading}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="mt-4 px-4 py-2 bg-accent hover:bg-blue-600 cursor-pointer text-white text-xs font-semibold rounded-md transition-colors"
          >
            {uploading ? 'Processing & Validating...' : 'Select File to Upload'}
          </label>
        </div>

        {/* Upload Messages */}
        {uploadResult && (
          <div className="p-4 bg-emerald-950/40 border border-emerald-800 rounded-md flex items-start space-x-3 text-xs text-emerald-300">
            <CheckCircle2 className="w-5 h-5 text-bullGreen shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">{uploadResult.message}</p>
              <p className="mt-1 text-gray-300">
                File: <strong>{uploadResult.filename}</strong> | Total rows: {uploadResult.total_records} | Valid OHLC: {uploadResult.valid_records}
              </p>
            </div>
          </div>
        )}

        {errorMsg && (
          <div className="p-4 bg-red-950/40 border border-red-800 rounded-md flex items-start space-x-3 text-xs text-red-300">
            <AlertCircle className="w-5 h-5 text-bearRed shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Ingestion Error</p>
              <p className="mt-1">{errorMsg}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DataManagement;
