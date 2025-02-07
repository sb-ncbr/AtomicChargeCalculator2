import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@acc2/components/ui/dropdown-menu";
import { Menu } from "lucide-react";
import { NavLink } from "react-router";

export const Nav = () => {
  return (
    <nav className="flex gap-4 items-center text-white">
      <div className="hidden gap-4 items-center text-white sm:flex">
        <NavLink
          to={"/"}
          className={({ isActive }) =>
            `${isActive ? "underline" : "no-underline"} hover:underline"`
          }
        >
          Home
        </NavLink>
        <NavLink
          to={"/calculations"}
          className={({ isActive }) =>
            `${isActive ? "underline" : "no-underline"} hover:underline`
          }
        >
          Calculations
        </NavLink>
        <NavLink to={"/login"} className={"hover:underline"}>
          Log in
        </NavLink>
      </div>
      <div className="block sm:hidden">
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
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <NavLink to={"/login"} className={"hover:underline"}>
                Log in
              </NavLink>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </nav>
  );
};
