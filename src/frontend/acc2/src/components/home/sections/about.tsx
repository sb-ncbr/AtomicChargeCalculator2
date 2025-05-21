import { baseApiUrl } from "@acc2/api/base";

import { Section } from "../section";

export const About = () => {
  return (
    <Section title="About">
      <p>
        Atomic Charge Calculator II (
        <span className="font-bold text-primary">ACC II</span>) is an
        application for fast calculation of partial atomic charges. It features{" "}
        <a
          href="methods.pdf"
          target="_blank"
          className="text-primary hover:underline"
        >
          20 empirical methods
        </a>{" "}
        along with parameters from literature.{" "}
        <a
          href="https://github.com/sb-ncbr/AtomicChargeCalculator2/wiki"
          target="_blank"
          className="text-primary hover:underline"
          rel="noreferrer"
        >
          Short introduction
        </a>{" "}
        covers the basic usage of ACC II. All methods and parameters are also
        available in a{" "}
        <a
          href="https://github.com/sb-ncbr/ChargeFW2"
          target="_blank"
          referrerPolicy="no-referrer"
          className="text-primary hover:underline"
          rel="noreferrer"
        >
          command-line application
        </a>{" "}
        and a{" "}
        <a
          href={`${baseApiUrl.replace("v1", "docs")}`}
          target="_blank"
          referrerPolicy="no-referrer"
          className="text-primary hover:underline"
          rel="noreferrer"
        >
          web API
        </a>{" "}
        that can be used in user workflows.
      </p>
    </Section>
  );
};
