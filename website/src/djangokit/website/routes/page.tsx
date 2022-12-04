/* Home Page */
import LinkContainer from "react-router-bootstrap/LinkContainer";
import { FaRocket } from "react-icons/fa";

import { usePageQuery } from "../api";
import PageComponent from "../components/page";
import IconButton from "../components/IconButton";

export default function Page() {
  const { isLoading, isError, data, error } = usePageQuery("home");
  return (
    <>
      <div className="d-flex flex-column gap-4 flex-md-row gap-md-5 h-100">
        <PageComponent
          isLoading={isLoading}
          isError={isError}
          data={data}
          error={error}
          className="flex-fill"
        />
        <div className="bg-dark p-4 rounded text-center">
          <LinkContainer to="/docs/get-started">
            <IconButton variant="outline-info" icon={<FaRocket />}>
              Get Started
            </IconButton>
          </LinkContainer>
        </div>
      </div>
    </>
  );
}
