/** FileConverterGuestNotice */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';

/**
 * FileConverterGuestNotice.
 * @example
 * const _ = true;
 */
export function FileConverterGuestNotice(props: FileConverterViewProps) {
  const { onRequestLogin } = props;
  return (
    <S.StatusBanner
      tone="warning"
      className="mt-3"
      data-testid="guest-loss-notice"
      action={
        <button
          type="button"
          className="underline underline-offset-2 font-medium"
          onClick={() => onRequestLogin?.()}
        >
          Sign in
        </button>
      }
    >
      {S.GUEST_LOSS_OF_PROGRESS_MESSAGE}
    </S.StatusBanner>
  );
}
