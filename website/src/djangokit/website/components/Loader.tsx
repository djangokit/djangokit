interface Props {
  children: any;
}

export default function Loader({ children }: Props) {
  return <div>{children}</div>;
}
