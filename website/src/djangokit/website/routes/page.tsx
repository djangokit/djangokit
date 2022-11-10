/* Home Page */
import { usePageQuery } from "../api";
import PageComponent from "../components/Page";

export default function Page() {
  const { isLoading, isError, data, error } = usePageQuery("home");
  return (
    <PageComponent
      isLoading={isLoading}
      isError={isError}
      data={data}
      error={error}
      className="flex-fill"
    />
  );
}
