/* Home Page */
import Button from "react-bootstrap/Button";
import LinkContainer from "react-router-bootstrap/LinkContainer";

import { usePageQuery } from "../api";
import PageComponent from "../components/page";
import { FaRocket } from "react-icons/fa";

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
          <Button className="d-flex align-items-center">
            <FaRocket className="me-1" />
            <span>Get Started</span>
          </Button>
        </LinkContainer>
      </div>
    </>
  );
}
