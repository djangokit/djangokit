import { default as BootstrapForm } from "react-bootstrap/Form";

declare const useCsrfContext;

/**
 * Form that includes a hidden form with the CSRF token. This should
 * generally always be used for forms.
 */
function Form({ children, ...props }: any) {
  const csrfToken = useCsrfContext();
  return (
    <BootstrapForm {...props}>
      <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
      {children}
    </BootstrapForm>
  );
}

export default Object.assign(Form, BootstrapForm);
