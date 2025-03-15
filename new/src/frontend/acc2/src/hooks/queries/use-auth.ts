import { AuthContext } from "@acc2/contexts/auth-context";
import { useContext } from "react";

export const useAuth = () => useContext(AuthContext);
