import Spinner from "react-bootstrap/Spinner";

interface Props {
  children: any;
}

export default function Loader({ children }: Props) {
  return (
    <div className="d-flex flex-column align-items-center gap-3 p-3">
      <Spinner />
      {children}
    </div>
  );
}
