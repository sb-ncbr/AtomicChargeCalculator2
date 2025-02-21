import { Outlet } from "react-router";
import { Header } from "./header/header";
import { Footer } from "./footer";

export const Layout = () => {
  return (
    <>
      <Header />
      <Outlet />
      <Footer />
    </>
  );
};
