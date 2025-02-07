import { NavLink } from "react-router";

export const Footer = () => {
  return (
    <footer className="w-full bg-primary px-8 py-4 text-white">
      <div className="max-w-content mx-auto">
        <span className="text-center text-xs block">© 2025 SB-NBCR</span>
        <div className="flex justify-between">
          <div>
            <ul>
              <li>
                <NavLink className="hover:underline" to={"/"}>
                  Home
                </NavLink>
              </li>
              <li>
                <NavLink className="hover:underline" to={"/calculations"}>
                  Calculations
                </NavLink>
              </li>
            </ul>
          </div>
          <div className="flex flex-col items-start">
            <NavLink
              className="hover:underline"
              to="https://webchem.ncbr.muni.cz/Platform/Home/TermsOfUse"
            >
              Terms of Use & GDPR
            </NavLink>
            <NavLink
              className="hover:underline"
              to="https://github.com/sb-ncbr/AtomicChargeCalculator2"
            >
              Github
            </NavLink>
            <NavLink className="hover:underline" to="https://ncbr.muni.cz/">
              SB-NBCR
            </NavLink>
          </div>
        </div>
      </div>
    </footer>
  );
};
