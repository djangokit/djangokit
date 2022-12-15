import { ANONYMOUS_USER, CsrfContext, CurrentUserContext } from "./context";

const csrfToken = process.argv[3] || "__csrf_token__";
const currentUser = process.argv[4]
  ? JSON.parse(process.argv[4])
  : ANONYMOUS_USER;

export default function Auth({ children }) {
  return (
    <CsrfContext.Provider value={csrfToken}>
      <CurrentUserContext.Provider value={currentUser}>
        {children}
      </CurrentUserContext.Provider>
    </CsrfContext.Provider>
  );
}
