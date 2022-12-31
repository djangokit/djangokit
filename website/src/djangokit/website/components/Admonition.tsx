interface Props {
  type?: "note" | "info" | "warning" | "danger";
  title?: string;
  className?: string;
  children: any;
}

export default function Admonition({
  type = "note",
  title = "Note",
  className = "",
  children,
}: Props) {
  let containerClassName = `admonition ${type}`;
  if (className) {
    containerClassName = `${containerClassName} ${className}`;
  }
  return (
    <div className={containerClassName}>
      <p className="admonition-title">{title}</p>
      {children}
    </div>
  );
}
