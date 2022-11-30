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
      <PageComponent
        isLoading={isLoading}
        isError={isError}
        data={data}
        error={error}
      />
      <div className="mt-5 d-flex align-items-center justify-content-center">
        <LinkContainer to="/docs/get-started">
          <IconButton icon={<FaRocket />}>Get Started</IconButton>
        </LinkContainer>
      </div>
    </>
  );
}
