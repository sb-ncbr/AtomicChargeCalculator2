import { Section } from "../section";
import ElixirLogo from "@acc2/assets/images/elixirlogo.png";

export const Elixir = () => {
  return (
    <Section separator={false}>
      <div className="flex flex-col items-center gap-4 mb-12">
        <img src={ElixirLogo} alt="Elixir logo" />
        <p>
          Atomic Charge Calculator II is a part of services provided by ELIXIR –
          European research infrastructure for biological information. For other
          services provided by ELIXIR's Czech Republic Node visit
          www.elixir-czech.cz/services .
        </p>
      </div>
    </Section>
  );
};
