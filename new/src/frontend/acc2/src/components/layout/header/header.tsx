import { Logo } from "@acc2/components/layout/header/logo";
import { Nav } from "./nav";

export const Header = () => {
  return (
    <header className="w-full px-8 h-header md:px-32 py-6 bg-primary shadow sticky top-0 z-50">
      <div className="max-w-content mx-auto flex gap-8 items-center">
        <a href="/">
          <Logo />
        </a>
        <Nav />
      </div>
    </header>
  );
};
