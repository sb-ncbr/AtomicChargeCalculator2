import { Section } from "../section";

export const About = () => {
  return (
    <Section title="About">
      <p>
        Atomic Charge Calculator II (
        <span className="font-bold text-primary">ACC II</span>) is an
        application for fast calculation of partial atomic charges. It features
        20 empirical methods along with parameters from literature. Short
        introduction covers the basic usage of ACC II. All methods and
        parameters are also available in a command-line{" "}
        <a
          href="https://github.com/sb-ncbr/ChargeFW2"
          target="_blank"
          referrerPolicy="no-referrer"
          className="text-primary hover:underline"
        >
          application
        </a>{" "}
        that can be used in user workflows.
      </p>
    </Section>
  );
};
