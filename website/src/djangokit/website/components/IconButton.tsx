import { default as Button } from "react-bootstrap/Button";
import Stack from "react-bootstrap/Stack";

/**
 * Button with icon on the left & other content on the right.
 */
export default function IconButton({
  icon,
  iconPosition = "left",
  gap = 2,
  children,
  ...props
}: any) {
  return (
    <Button {...props}>
      <Stack direction="horizontal" gap={gap} className="text-nowrap">
        {iconPosition === "left" ? icon : null}
        {children?.length ? <div>{children}</div> : null}
        {iconPosition === "right" ? icon : null}
      </Stack>
    </Button>
  );
}
