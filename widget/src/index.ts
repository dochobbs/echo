/**
 * @meded/echo-widget
 *
 * AI Tutor widget for the MedEd platform.
 *
 * @example
 * import { EchoWidget } from '@meded/echo-widget';
 * import '@meded/echo-widget/styles.css';
 *
 * function App() {
 *   return (
 *     <EchoWidget
 *       apiUrl="https://echo.meded.app"
 *       context={{
 *         source: 'oread',
 *         patient: currentPatient,
 *         learnerLevel: 'resident',
 *       }}
 *     />
 *   );
 * }
 */

// Styles (bundled separately as styles.css)
import './styles/echo.css';

// Components
export { EchoWidget, EchoIcon, EchoPanel } from './components';

// Hooks
export { useEchoApi, useEchoMemory } from './hooks';

// Types
export type {
  EchoWidgetProps,
  EchoSource,
  EchoVoice,
  EchoMessage,
  EchoMemoryItem,
  EchoContext,
  PatientContext,
  EncounterContext,
  FeedbackRequest,
  FeedbackResponse,
  QuestionRequest,
  SpeakRequest,
  VoiceInfo,
} from './types';

// Styles - users should import separately:
// import '@meded/echo-widget/styles.css';
