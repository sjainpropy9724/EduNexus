import React, { useState } from 'react';
import axios from 'axios';
import { UploadCloud, FileText, CheckCircle, XCircle, Loader } from 'lucide-react';

const SyllabusUploader = () => {
  const [file,   setFile]   = useState(null);
  const [status, setStatus] = useState('idle');
  const [message,setMessage]= useState('');

  const handleFileChange = (e) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
      setStatus('idle');
      setMessage('');
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setStatus('uploading');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(
        'http://127.0.0.1:8001/api/v1/ingest/syllabus',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      setStatus('success');
      setMessage(`✅ Ingested: ${file.name} — ${response.data.graph_stats?.nodes_created || 0} concepts added to graph.`);
      setFile(null);
    } catch (err) {
      setStatus('error');
      setMessage(err.response?.data?.detail || 'Upload failed. Check backend logs.');
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <div className="border-2 border-dashed border-gray-200 rounded-lg p-6 text-center bg-gray-50 hover:bg-gray-100 transition-colors">
        <input
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          className="hidden"
          id="file-upload"
        />
        <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
          <FileText className="text-gray-300 mb-2" size={36}/>
          <span className="text-gray-600 font-medium text-sm">
            {file ? file.name : 'Click to select a Syllabus PDF'}
          </span>
          <span className="text-gray-400 text-xs mt-1">PDF only • max 10MB</span>
        </label>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center gap-2 flex-1 mr-4">
          {status === 'success'   && <CheckCircle className="text-green-500 shrink-0" size={16}/>}
          {status === 'error'     && <XCircle     className="text-red-500 shrink-0"   size={16}/>}
          {status === 'uploading' && <Loader      className="text-blue-500 animate-spin shrink-0" size={16}/>}
          <span className={`text-xs ${
            status === 'success' ? 'text-green-600'
            : status === 'error' ? 'text-red-600'
            : 'text-gray-500'
          }`}>
            {message || 'Select a PDF syllabus to ingest into the knowledge graph'}
          </span>
        </div>
        <button
          onClick={handleUpload}
          disabled={!file || status === 'uploading'}
          className="bg-slate-800 text-white px-5 py-2 rounded-lg hover:bg-slate-900 disabled:opacity-40 disabled:cursor-not-allowed text-sm font-semibold transition-all shrink-0"
        >
          {status === 'uploading' ? 'Processing...' : 'Process Syllabus'}
        </button>
      </div>
    </div>
  );
};

export default SyllabusUploader;
