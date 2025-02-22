import { Section } from "../section";
import ElixirLogo from "@acc2/assets/images/elixirlogo.png";

export const Elixir = () => {
  return (
    <Section separator={false}>
      <div className="flex flex-col items-center gap-4 mb-12">
        <a
          href="https://www.elixir-czech.cz/services"
          target="_blank"
          rel="noreferrer"
        >
          <img src={ElixirLogo} alt="Elixir logo" />
        </a>
        <p>
          Atomic Charge Calculator II is a part of services provided by ELIXIR –
          European research infrastructure for biological information. For other
          services provided by ELIXIR's Czech Republic Node visit{" "}
          <a
            href="https://www.elixir-czech.cz/services"
            target="_blank"
            rel="noreferrer"
            className="text-primary hover:underline"
          >
            www.elixir-czech.cz/services
          </a>
          .
        </p>
      </div>
    </Section>
  );
};
