import React from 'react';
import ReactDOM from 'react-dom/client';
import { EchoWidget } from '../src';
import '../src/styles/echo.css';

// Demo patient context (matching the HTML page)
const demoPatient = {
  patientId: 'demo-001',
  name: 'Emma Thompson',
  age: 8,
  sex: 'female' as const,
  chiefComplaint: 'Sore throat x 3 days',
  allergies: ['Penicillin (rash)'],
  medications: [],
  problemList: [],
};

function Demo() {
  return (
    <EchoWidget
      apiUrl="http://localhost:8002"
      context={{
        source: 'oread',
        patient: demoPatient,
        learnerLevel: 'resident',
      }}
      position="bottom-right"
      defaultVoice="eryn"
      theme="light"
      onResponse={(msg) => console.log('Echo response:', msg)}
      onToggle={(isOpen) => console.log('Widget toggled:', isOpen)}
    />
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Demo />
  </React.StrictMode>
);
