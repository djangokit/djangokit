/* Page */
import { useParams } from "react-router";
import { usePageQuery } from "../../api";
import PageComponent from "../../components/Page";

export default function Page() {
  const { slug } = useParams();
  const { isLoading, isError, data, error } = usePageQuery(slug ?? "404");
  return (
    <PageComponent
      isLoading={isLoading}
      isError={isError}
      data={data}
      error={error}
      className="p-3"
    />
  );
}
