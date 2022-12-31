import { ANONYMOUS_USER, CurrentUserContext } from "./context";

const currentUser = process.argv[3]
  ? JSON.parse(process.argv[3])
  : ANONYMOUS_USER;

export default function Auth({ children }) {
  return (
    <CurrentUserContext.Provider value={currentUser}>
      {children}
    </CurrentUserContext.Provider>
  );
}
