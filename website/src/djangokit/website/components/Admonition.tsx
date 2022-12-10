interface Props {
  type?: "note" | "info" | "warning" | "danger";
  title?: string;
  children: any;
}

export default function Admonition({
  type = "note",
  title = "Note",
  children,
}: Props) {
  return (
    <div className={`admonition ${type}`}>
      <p className="admonition-title">{title}</p>
      {children}
    </div>
  );
}
