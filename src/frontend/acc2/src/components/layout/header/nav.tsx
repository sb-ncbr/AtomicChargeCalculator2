import { baseApiUrl } from "@acc2/api/base";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@acc2/components/ui/dropdown-menu";
import { useAuth } from "@acc2/lib/hooks/queries/use-auth";
import { Menu } from "lucide-react";
import { NavLink } from "react-router";

import LoginImg from "../../../assets/images/button-login.svg";

export const Nav = () => {
  const { isAuthenticated } = useAuth();

  const onLoginClick = () => {
    window.location.href = `${baseApiUrl}/auth/login`;
  };

  const onLogoutClick = async () => {
    window.location.href = `${baseApiUrl}/auth/logout`;
  };

  return (
    <nav className="flex gap-4 items-center text-white w-full">
      <div className="hidden gap-4 items-center justify-between text-white sm:flex w-full">
        <div className="flex gap-4 grow">
          <NavLink
            to={"/"}
            className={({ isActive }) =>
              `${isActive ? "underline" : "no-underline"} hover:underline"`
            }
          >
            Home
          </NavLink>
          {isAuthenticated && (
            <>
              <NavLink
                to={"/calculations"}
                className={({ isActive }) =>
                  `${isActive ? "underline" : "no-underline"} hover:underline`
                }
              >
                Calculations
              </NavLink>
              <NavLink
                to={"/files"}
                className={({ isActive }) =>
                  `${isActive ? "underline" : "no-underline"} hover:underline`
                }
              >
                Files
              </NavLink>
            </>
          )}
        </div>
        {/* checking explicitly for false so that the button does not blink */}
        {isAuthenticated === false && (
          <button className="ml-auto hover:scale-105" onClick={onLoginClick}>
            <img src={LoginImg} alt="Login Button" width={150} />
          </button>
        )}
        {isAuthenticated && (
          <button className="hover:underline" onClick={onLogoutClick}>
            Logout
          </button>
        )}
      </div>
      <div className="block sm:hidden ml-auto">
        <DropdownMenu>
          <DropdownMenuTrigger>
            <Menu />
          </DropdownMenuTrigger>
          <DropdownMenuContent className="mr-4">
            <DropdownMenuItem>
              <NavLink
                to={"/"}
                className={({ isActive }) =>
                  `${isActive ? "underline" : "no-underline"}`
                }
              >
                Home
              </NavLink>
            </DropdownMenuItem>
            {isAuthenticated && (
              <>
                <DropdownMenuItem className="relative">
                  <NavLink
                    to={"/calculations"}
                    className={({ isActive }) =>
                      `${isActive ? "underline" : "no-underline"}`
                    }
                  >
                    Calculations
                  </NavLink>
                </DropdownMenuItem>
                <DropdownMenuItem className="relative">
                  <NavLink
                    to={"/files"}
                    className={({ isActive }) =>
                      `${isActive ? "underline" : "no-underline"}`
                    }
                  >
                    Files
                  </NavLink>
                </DropdownMenuItem>
              </>
            )}
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              {isAuthenticated === false && (
                <button onClick={onLoginClick}>
                  <img
                    src={LoginImg}
                    alt="Login Button"
                    height={10}
                    width={150}
                  />
                </button>
              )}
              {isAuthenticated && (
                <button onClick={onLogoutClick}>Logout</button>
              )}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </nav>
  );
};
