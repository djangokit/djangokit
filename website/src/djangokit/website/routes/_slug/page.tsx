/* Page */
import { useParams } from "react-router-dom";
import { usePageQuery } from "../../api";
import PageComponent from "../../components/page";

export default function Page() {
  const { slug } = useParams();
  const { isLoading, isError, data, error } = usePageQuery(slug ?? "404");
  return (
    <PageComponent
      isLoading={isLoading}
      isError={isError}
      data={data}
      error={error}
    />
  );
}
