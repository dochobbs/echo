import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { api, ImportedPatient } from '../api/client';
import { UploadIcon, TrashIcon, UserIcon } from '../components/icons';

export function Patients() {
  const [patients, setPatients] = useState<ImportedPatient[]>([]);
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      const response = await api.getPatients();
      setPatients(response.patients);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load patients');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setImporting(true);
    setError(null);
    setSuccess(null);

    try {
      if (files.length === 1) {
        const response = await api.importPatient(files[0]);
        setPatients(prev => [...prev, response.patient]);
        setSuccess(`Imported ${response.patient.name}`);
        
        if (response.parse_warnings.length > 0) {
          console.log('Parse warnings:', response.parse_warnings);
        }
      } else {
        const fileArray = Array.from(files);
        const response = await api.bulkImportPatients(fileArray);
        
        const newPatients = response.results
          .filter(r => r.success && r.patient)
          .map(r => r.patient!);
        
        setPatients(prev => [...prev, ...newPatients]);
        
        if (response.failed > 0) {
          const failedFiles = response.results
            .filter(r => !r.success)
            .map(r => r.filename)
            .join(', ');
          setError(`Failed to import ${response.failed} file(s): ${failedFiles}`);
        }
        
        if (response.successful > 0) {
          setSuccess(`Successfully imported ${response.successful} patient${response.successful > 1 ? 's' : ''}`);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to import patient(s)');
    } finally {
      setImporting(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDelete = async (patientId: string, patientName: string) => {
    if (!confirm(`Remove ${patientName} from your patient panel?`)) return;

    try {
      await api.deletePatient(patientId);
      setPatients(prev => prev.filter(p => p.id !== patientId));
      setSuccess(`Removed ${patientName}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete patient');
    }
  };

  const formatAge = (ageMonths?: number) => {
    if (!ageMonths) return 'Unknown age';
    if (ageMonths < 12) return `${ageMonths} months`;
    const years = Math.floor(ageMonths / 12);
    const months = ageMonths % 12;
    if (months === 0) return `${years} year${years > 1 ? 's' : ''}`;
    return `${years}y ${months}m`;
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-2xl font-semibold text-gray-100 mb-2">Patient Panel</h1>
        <p className="text-gray-400">Import patient records from C-CDA files to practice with real-world data.</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mb-6"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".xml,.cda,.ccda"
          multiple
          onChange={handleFileSelect}
          className="hidden"
          id="ccda-upload"
        />
        <label
          htmlFor="ccda-upload"
          className={`card flex items-center justify-center gap-3 p-6 cursor-pointer border-2 border-dashed border-surface-4 hover:border-echo-500/50 transition-colors ${importing ? 'opacity-50 pointer-events-none' : ''}`}
        >
          {importing ? (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              className="w-6 h-6 border-2 border-echo-500 border-t-transparent rounded-full"
            />
          ) : (
            <UploadIcon size={24} className="text-gray-400" />
          )}
          <span className="text-gray-300">
            {importing ? 'Importing...' : 'Upload C-CDA Files'}
          </span>
        </label>
        <p className="text-xs text-gray-500 mt-2 text-center">
          Accepts .xml, .cda, or .ccda files (select multiple for bulk upload)
        </p>
      </motion.div>

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm"
          >
            {error}
          </motion.div>
        )}
        {success && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-4 p-3 bg-green-500/10 border border-green-500/20 rounded-xl text-green-400 text-sm"
          >
            {success}
          </motion.div>
        )}
      </AnimatePresence>

      {loading ? (
        <div className="flex justify-center py-12">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="w-8 h-8 border-2 border-echo-500 border-t-transparent rounded-full"
          />
        </div>
      ) : patients.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <UserIcon size={48} className="mx-auto text-gray-600 mb-4" />
          <p className="text-gray-400">No patients imported yet</p>
          <p className="text-gray-500 text-sm mt-1">Upload a C-CDA file to get started</p>
        </motion.div>
      ) : (
        <div className="space-y-3">
          {patients.map((patient, index) => (
            <motion.div
              key={patient.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="card p-4"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-medium text-gray-100">{patient.name}</h3>
                  <p className="text-sm text-gray-400">
                    {formatAge(patient.age_months)}
                    {patient.sex && ` · ${patient.sex}`}
                  </p>
                  
                  {patient.problems.length > 0 && (
                    <div className="mt-2">
                      <p className="text-xs text-gray-500 mb-1">Active Problems:</p>
                      <div className="flex flex-wrap gap-1">
                        {patient.problems.filter(p => p.status === 'active').slice(0, 3).map((problem, i) => (
                          <span key={i} className="text-xs px-2 py-0.5 bg-surface-3 rounded-full text-gray-300">
                            {problem.display}
                          </span>
                        ))}
                        {patient.problems.filter(p => p.status === 'active').length > 3 && (
                          <span className="text-xs px-2 py-0.5 bg-surface-3 rounded-full text-gray-500">
                            +{patient.problems.filter(p => p.status === 'active').length - 3} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {patient.allergies.length > 0 && (
                    <div className="mt-2">
                      <p className="text-xs text-gray-500 mb-1">Allergies:</p>
                      <div className="flex flex-wrap gap-1">
                        {patient.allergies.slice(0, 2).map((allergy, i) => (
                          <span key={i} className="text-xs px-2 py-0.5 bg-red-500/10 border border-red-500/20 rounded-full text-red-400">
                            {allergy.display}
                          </span>
                        ))}
                        {patient.allergies.length > 2 && (
                          <span className="text-xs px-2 py-0.5 bg-surface-3 rounded-full text-gray-500">
                            +{patient.allergies.length - 2} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                <motion.button
                  onClick={() => handleDelete(patient.id, patient.name)}
                  className="p-2 text-gray-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <TrashIcon size={18} />
                </motion.button>
              </div>

              <div className="mt-3 pt-3 border-t border-surface-3 flex items-center justify-between text-xs text-gray-500">
                <span>Imported from {patient.source_file || patient.source}</span>
                <span>{new Date(patient.imported_at).toLocaleDateString()}</span>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
