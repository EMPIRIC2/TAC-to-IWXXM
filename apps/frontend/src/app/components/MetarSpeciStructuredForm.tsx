/**
 * Structured METAR/SPECI entry form (WMO-No. 782 group order) → TAC text.
 *
 * Inserts into the workbench free-text path and uses the same convert pipeline.
 */

import { useId, useMemo, useState } from 'react';
import {
  buildMetarSpeciTac,
  type MetarSpeciFormState,
} from './metarSpeciStructuredTac';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';

export type MetarSpeciStructuredFormProps = {
  /** Called with assembled TAC for the free-text converter input. */
  onInsertTac: (tac: string) => void;
  /** Optional: insert TAC then run the existing convert action. */
  onConvertWithTac?: (tac: string) => void;
  /** Live lint issues for a short summary under the form. */
  lintIssues?: Array<{ code: string; severity: string; message: string }>;
  /** Initial product selection. */
  defaultProduct?: 'METAR' | 'SPECI';
  /** Disable controls when the session is read-only. */
  disabled?: boolean;
};

const INITIAL: MetarSpeciFormState = {
  product: 'METAR',
  cor: false,
  auto: false,
  nil: false,
  cccc: '',
  dayTime: '',
  wind: '',
  visibility: '',
  rvr: '',
  weather: '',
  cloud: '',
  temperature: '',
  qnh: '',
  supplementary: '',
  rmk: '',
  includeRmk: true,
};

const INPUT_CLASS =
  'mt-1 h-8 w-full rounded-md border border-gray-300 bg-white px-2 font-mono text-sm text-gray-900 dark:border-gray-600 dark:bg-gray-800 dark:text-white';

type FieldSetter = (
  key: keyof MetarSpeciFormState,
) => (value: string | boolean) => void;

type FieldProps = {
  id: string;
  label: string;
  value: string;
  onChange: (v: string) => void;
  testId: string;
  placeholder?: string;
  disabled?: boolean;
};

/**
 * Labeled monospace input for one METAR/SPECI group.
 *
 * @param props - Field identity, value, and change handler
 */
function Field(props: FieldProps) {
  return (
    <div>
      <Label htmlFor={props.id} className="text-sm text-gray-800 dark:text-gray-200">
        {props.label}
      </Label>
      <Input
        id={props.id}
        className={INPUT_CLASS}
        value={props.value}
        disabled={props.disabled}
        onChange={(e) => props.onChange(e.target.value)}
        data-testid={props.testId}
        placeholder={props.placeholder}
      />
    </div>
  );
}

type HeaderFieldsProps = {
  baseId: string;
  state: MetarSpeciFormState;
  disabled: boolean;
  set: FieldSetter;
};

/**
 * Product, modifiers, station, and observation time.
 *
 * @param props - Form header state
 */
function HeaderFields({ baseId, state, disabled, set }: HeaderFieldsProps) {
  return (
    <>
      <label
        className="text-sm text-gray-800 dark:text-gray-200"
        htmlFor={`${baseId}-product`}
      >
        Product
        <select
          id={`${baseId}-product`}
          className={INPUT_CLASS}
          data-testid="structured-product"
          disabled={disabled}
          value={state.product}
          onChange={(e) => set('product')(e.target.value as 'METAR' | 'SPECI')}
        >
          <option value="METAR">METAR</option>
          <option value="SPECI">SPECI</option>
        </select>
      </label>
      <div className="flex flex-wrap items-end gap-3 text-sm text-gray-800 dark:text-gray-200">
        <label className="inline-flex items-center gap-1">
          <input
            type="checkbox"
            checked={state.cor}
            disabled={disabled}
            onChange={(e) => set('cor')(e.target.checked)}
            data-testid="structured-cor"
          />
          COR
        </label>
        <label className="inline-flex items-center gap-1">
          <input
            type="checkbox"
            checked={state.auto}
            disabled={disabled || state.nil}
            onChange={(e) => set('auto')(e.target.checked)}
            data-testid="structured-auto"
          />
          AUTO
        </label>
        <label className="inline-flex items-center gap-1">
          <input
            type="checkbox"
            checked={state.nil}
            disabled={disabled}
            onChange={(e) => {
              set('nil')(e.target.checked);
              if (e.target.checked) {
                set('auto')(false);
              }
            }}
            data-testid="structured-nil"
          />
          NIL
        </label>
      </div>
      <Field
        id={`${baseId}-cccc`}
        label="Station (CCCC)"
        value={state.cccc}
        onChange={set('cccc')}
        testId="structured-cccc"
        placeholder="LUDO"
        disabled={disabled}
      />
      <Field
        id={`${baseId}-time`}
        label="Day and time (YYGGggZ)"
        value={state.dayTime}
        onChange={set('dayTime')}
        testId="structured-daytime"
        placeholder="211025Z"
        disabled={disabled}
      />
    </>
  );
}

type ObservationFieldsProps = {
  baseId: string;
  state: MetarSpeciFormState;
  disabled: boolean;
  set: FieldSetter;
};

/**
 * Body groups after station/time when the report is not NIL.
 *
 * @param props - Form state and field setter
 */
function ObservationFields({ baseId, state, disabled, set }: ObservationFieldsProps) {
  const cavok = state.visibility.trim().toUpperCase() === 'CAVOK';
  return (
    <>
      <Field
        id={`${baseId}-wind`}
        label="Surface wind"
        value={state.wind}
        onChange={set('wind')}
        testId="structured-wind"
        placeholder="31015G27KT 280V350"
        disabled={disabled}
      />
      <Field
        id={`${baseId}-vis`}
        label="Prevailing visibility or CAVOK"
        value={state.visibility}
        onChange={set('visibility')}
        testId="structured-visibility"
        placeholder="4000"
        disabled={disabled}
      />
      <Field
        id={`${baseId}-rvr`}
        label="Runway visual range"
        value={state.rvr}
        onChange={set('rvr')}
        testId="structured-rvr"
        placeholder="R24/P2000"
        disabled={disabled}
      />
      <Field
        id={`${baseId}-wx`}
        label="Present weather"
        value={state.weather}
        onChange={set('weather')}
        testId="structured-weather"
        placeholder="+SHRA"
        disabled={disabled || cavok}
      />
      <Field
        id={`${baseId}-cloud`}
        label="Cloud or vertical visibility"
        value={state.cloud}
        onChange={set('cloud')}
        testId="structured-cloud"
        placeholder="FEW005 SCT018"
        disabled={disabled || cavok}
      />
      <Field
        id={`${baseId}-temp`}
        label="Air and dew-point temperature"
        value={state.temperature}
        onChange={set('temperature')}
        testId="structured-temperature"
        placeholder="10/03"
        disabled={disabled}
      />
      <Field
        id={`${baseId}-qnh`}
        label="Pressure QNH"
        value={state.qnh}
        onChange={set('qnh')}
        testId="structured-qnh"
        placeholder="Q0995"
        disabled={disabled}
      />
      <Field
        id={`${baseId}-supp`}
        label="Supplementary information"
        value={state.supplementary}
        onChange={set('supplementary')}
        testId="structured-supplementary"
        placeholder="RERA WS R24"
        disabled={disabled}
      />
    </>
  );
}

type RemarksBlockProps = {
  baseId: string;
  state: MetarSpeciFormState;
  disabled: boolean;
  set: FieldSetter;
};

/**
 * National remarks field and include-RMK toggle.
 *
 * @param props - Remarks state
 */
function RemarksBlock({ baseId, state, disabled, set }: RemarksBlockProps) {
  return (
    <div className="sm:col-span-2">
      <Field
        id={`${baseId}-rmk`}
        label="National remarks (after RMK)"
        value={state.rmk}
        onChange={set('rmk')}
        testId="structured-rmk"
        placeholder="optional national text"
        disabled={disabled || !state.includeRmk || state.nil}
      />
      <label className="mt-1 inline-flex items-center gap-1.5 text-xs text-gray-700 dark:text-gray-300">
        <input
          type="checkbox"
          data-testid="structured-include-rmk"
          disabled={disabled || state.nil}
          checked={state.includeRmk}
          onChange={(e) => set('includeRmk')(e.target.checked)}
        />
        Include RMK in TAC (national remarks are not for international dissemination)
      </label>
    </div>
  );
}

type ActionsProps = {
  disabled: boolean;
  canSubmit: boolean;
  tac: string;
  onInsertTac: (tac: string) => void;
  onConvertWithTac?: (tac: string) => void;
};

/**
 * Insert / convert actions for the assembled TAC.
 *
 * @param props - Callbacks and enablement
 */
function FormActions({
  disabled,
  canSubmit,
  tac,
  onInsertTac,
  onConvertWithTac,
}: ActionsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      <Button
        type="button"
        size="sm"
        variant="outline"
        disabled={disabled || !canSubmit}
        data-testid="structured-insert-tac"
        onClick={() => onInsertTac(tac)}
      >
        Insert TAC
      </Button>
      {onConvertWithTac ? (
        <Button
          type="button"
          size="sm"
          disabled={disabled || !canSubmit}
          data-testid="structured-convert-tac"
          onClick={() => onConvertWithTac(tac)}
        >
          Convert with this TAC
        </Button>
      ) : null}
    </div>
  );
}

/**
 * Operator form for METAR/SPECI groups in WMO handbook order.
 *
 * @param props - Insert / convert callbacks and defaults
 */
export function MetarSpeciStructuredForm({
  onInsertTac,
  onConvertWithTac,
  lintIssues = [],
  defaultProduct = 'METAR',
  disabled = false,
}: MetarSpeciStructuredFormProps) {
  const baseId = useId();
  const [state, setState] = useState<MetarSpeciFormState>({
    ...INITIAL,
    product: defaultProduct,
  });
  const tacPreview = useMemo(() => buildMetarSpeciTac(state), [state]);
  const canSubmit = Boolean(state.cccc.trim() && state.dayTime.trim());
  const set: FieldSetter = (key) => (value) =>
    setState((prev) => ({ ...prev, [key]: value }));

  return (
    <div className="space-y-3" data-testid="metar-speci-structured-form">
      <div className="flex flex-wrap items-center gap-2">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Enter METAR or SPECI groups in handbook order, then send the TAC to the same
          converter as free-text entry.
        </p>
        <span className="rounded border border-blue-300 px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-blue-700 dark:border-blue-600 dark:text-blue-300">
          Beta
        </span>
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        <HeaderFields baseId={baseId} state={state} disabled={disabled} set={set} />
        {!state.nil ? (
          <ObservationFields
            baseId={baseId}
            state={state}
            disabled={disabled}
            set={set}
          />
        ) : null}
        <RemarksBlock baseId={baseId} state={state} disabled={disabled} set={set} />
      </div>

      <div
        className="rounded-md border border-gray-200 bg-white px-2 py-1.5 font-mono text-xs text-gray-800 dark:border-gray-700 dark:bg-gray-950 dark:text-gray-100"
        data-testid="structured-tac-preview"
        aria-live="polite"
      >
        {canSubmit ? tacPreview : 'Enter station and day/time to build TAC.'}
      </div>

      {lintIssues.length > 0 ? (
        <ul
          className="list-disc space-y-0.5 pl-5 text-xs text-gray-700 dark:text-gray-300"
          data-testid="structured-lint-summary"
        >
          {lintIssues.slice(0, 8).map((issue) => (
            <li key={`${issue.code}-${issue.message}`}>
              <span className="font-medium uppercase">{issue.severity}</span>:{' '}
              {issue.message}
            </li>
          ))}
        </ul>
      ) : null}

      <FormActions
        disabled={disabled}
        canSubmit={canSubmit}
        tac={tacPreview}
        onInsertTac={onInsertTac}
        onConvertWithTac={onConvertWithTac}
      />
    </div>
  );
}
