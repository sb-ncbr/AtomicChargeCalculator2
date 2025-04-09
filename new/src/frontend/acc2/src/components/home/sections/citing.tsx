import { Section } from "../section";

export const Citing = () => {
  return (
    <Section title="Citing">
      <p>
        If you found Atomic Charge Calculator II helpful, please cite:{" "}
        <i>
          Raček, T., Schindler, O., Toušek, D., Horský, V., Berka, K., Koča, J.,
          & Svobodová, R. (2020).{" "}
          <a
            href="https://doi.org/10.1093/nar/gkaa367"
            target="_blank"
            referrerPolicy="no-referrer"
            className="text-primary hover:underline" rel="noreferrer"
          >
            Atomic Charge Calculator II: web-based tool for the calculation of
            partial atomic charges
          </a>
          . Nucleic Acids Research.
        </i>{" "}
        Are you interested in a research collaboration? Feel free to{" "}
        <a
          href="mailto:krab1k@mail.muni.cz"
          target="_blank"
          referrerPolicy="no-referrer"
          className="text-primary hover:underline" rel="noreferrer"
        >
          contact us
        </a>
        .
      </p>
    </Section>
  );
};
