# Echo Widget Integration

Embed Echo in your MedEd application (Oread, Syrinx, or Mneme).

## Installation

```bash
npm install @meded/echo-widget
# or
yarn add @meded/echo-widget
```

## Basic Setup

Add to your app (e.g., in `_app.tsx` or layout component):

```tsx
import { EchoWidget } from '@meded/echo-widget';
import '@meded/echo-widget/styles.css';

function MyApp({ Component, pageProps }) {
  return (
    <>
      <Component {...pageProps} />

      <EchoWidget
        apiUrl="http://localhost:8001"  // or production URL
        context={{
          source: 'oread',  // or 'syrinx' or 'mneme'
        }}
      />
    </>
  );
}
```

## With Patient Context

When patient data is available:

```tsx
<EchoWidget
  apiUrl="http://localhost:8001"
  context={{
    source: 'oread',
    patient: {
      patientId: patient.id,
      name: patient.name,
      age: patient.age,
      chiefComplaint: patient.chiefComplaint,
    },
    learnerLevel: 'resident',
  }}
  defaultVoice="eryn"
  position="bottom-right"  // bottom-left, top-right, top-left
  theme="system"           // light, dark, system
/>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `apiUrl` | string | required | Echo API endpoint |
| `context` | object | required | Source and patient context |
| `defaultVoice` | string | `"eryn"` | Eleven Labs voice ID |
| `position` | string | `"bottom-right"` | Widget position |
| `theme` | string | `"system"` | Color theme |

### Available Voices

| Voice | Description |
|-------|-------------|
| `eryn` | Calm, confident (default) |
| `matilda` | Warm, friendly |
| `clarice` | Clear, professional |
| `clara` | Approachable |
| `devan` | Energetic |
| `lilly` | Gentle |

## Local Development

The widget package isn't published to npm yet. For local development:

### Option 1: npm link

```bash
# In echo/widget
npm link

# In host app (oread, syrinx, mneme)
npm link @meded/echo-widget
```

### Option 2: Relative path

In the host app's `package.json`:

```json
{
  "dependencies": {
    "@meded/echo-widget": "file:../echo/widget"
  }
}
```

## Context Object

The `context` prop accepts:

```typescript
interface EchoContext {
  source: 'oread' | 'syrinx' | 'mneme';
  patient?: {
    patientId: string;
    name: string;
    age: number | string;
    sex?: string;
    chiefComplaint?: string;
    problemList?: string[];
    medications?: string[];
    allergies?: string[];
  };
  learnerLevel?: 'student' | 'resident' | 'np_student' | 'fellow' | 'attending';
  encounter?: {
    type: string;
    phase: string;
  };
}
```

## Example: Oread Integration

```tsx
// In oread/web/components/PatientView.tsx

import { EchoWidget } from '@meded/echo-widget';
import '@meded/echo-widget/styles.css';

export function PatientView({ patient }) {
  return (
    <div>
      {/* Patient details */}
      <PatientHeader patient={patient} />
      <EncounterList encounters={patient.encounters} />

      {/* Echo widget */}
      <EchoWidget
        apiUrl={process.env.NEXT_PUBLIC_ECHO_URL}
        context={{
          source: 'oread',
          patient: {
            patientId: patient.id,
            name: patient.demographics.fullName,
            age: patient.demographics.ageYears,
            sex: patient.demographics.sex,
            problemList: patient.problemList.map(p => p.displayName),
            medications: patient.medicationList.map(m => m.displayName),
            allergies: patient.allergyList.map(a => a.displayName),
          },
          learnerLevel: 'np_student',
        }}
        position="bottom-right"
      />
    </div>
  );
}
```

## Example: Syrinx Integration

```tsx
// During voice encounter

<EchoWidget
  apiUrl={process.env.NEXT_PUBLIC_ECHO_URL}
  context={{
    source: 'syrinx',
    patient: patientContext,
    encounter: {
      type: 'acute',
      phase: currentPhase,  // 'history', 'exam', 'assessment', 'plan'
    },
    learnerLevel: 'resident',
  }}
  position="top-right"
  theme="dark"
/>
```

## Example: Mneme Integration

```tsx
// In EMR chart view

<EchoWidget
  apiUrl={process.env.NEXT_PUBLIC_ECHO_URL}
  context={{
    source: 'mneme',
    patient: {
      patientId: chart.patientId,
      name: chart.patientName,
      age: chart.age,
      problemList: chart.conditions.map(c => c.displayName),
      allergies: chart.allergies.map(a => a.displayName),
    },
  }}
  position="bottom-left"
/>
```
