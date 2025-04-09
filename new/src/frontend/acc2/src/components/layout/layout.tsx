import { Outlet } from "react-router";

import { Footer } from "./footer";
import { Header } from "./header/header";

export const Layout = () => {
  return (
    <>
      <Header />
      <Outlet />
      <Footer />
    </>
  );
};
