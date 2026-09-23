import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export function Field({
  id,
  label,
  required,
  error,
  multiline,
  ...props
}: {
  id: string;
  label: string;
  required?: boolean;
  error?: string;
  multiline?: boolean;
} & React.InputHTMLAttributes<HTMLInputElement> &
  React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  const inputProps = { id, error, ...props } as Record<string, unknown>;
  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-sm font-medium text-foreground">
        {label} {required && <span className="text-danger">*</span>}
      </label>
      {multiline ? (
        <Textarea {...(inputProps as React.TextareaHTMLAttributes<HTMLTextAreaElement>)} />
      ) : (
        <Input {...(inputProps as React.InputHTMLAttributes<HTMLInputElement>)} />
      )}
      {error && (
        <p id={`${id}-error`} className="mt-1 text-xs text-danger" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
