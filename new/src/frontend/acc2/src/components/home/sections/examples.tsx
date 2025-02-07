import Propofol from "@acc2/assets/images/propofol.png";
import Bax from "@acc2/assets/images/bax.png";
import Receptor from "@acc2/assets/images/receptor.png";
import { Example } from "../example";
import { Section } from "../section";

export const Examples = () => {
  return (
    <Section title="Examples">
      <div className="grid grid-cols-1 gap-8 h-full xl:grid-cols-3">
        <Example
          title="Dissociating hydrogens"
          image={{ src: Propofol, alt: "Propofol" }}
          actions={[{ name: "Phenols", action: () => {} }]}
        >
          <p>
            This example focuses on acid dissociation of seven phenolic drugs,
            described in{" "}
            <a
              href="https://www.drugbank.ca/"
              target="_blank"
              referrerPolicy="no-referrer"
              className="text-primary hover:underline"
            >
              DrugBank
            </a>
            . Their structures were obtained from{" "}
            <a
              href="https://pubchem.ncbi.nlm.nih.gov/"
              target="_blank"
              referrerPolicy="no-referrer"
              className="text-primary hover:underline"
            >
              PubChem
            </a>
            . During the acid dissociation, these compounds release a hydrogen
            from the phenolic OH group. Using ACC II, we can examine a relation
            between pKa and a charge on the dissociating hydrogen. We found that
            the higher is pKa, the lower charge the hydrogen has (see table).
            This finding agrees with results published in{" "}
            <a
              href="https://pubs.acs.org/doi/full/10.1021/ci200133w"
              target="_blank"
              referrerPolicy="no-referrer"
              className="text-primary hover:underline"
            >
              literature
            </a>
            .
          </p>
        </Example>
        <Example
          title="Apoptotic protein activation"
          image={{ src: Bax, alt: "Bax" }}
          actions={[
            { name: "Activated", action: () => {} },
            { name: "Inactive", action: () => {} },
          ]}
        >
          <p>
            BAX protein regulates an apoptosis process. In our example, we show
            inactive BAX (PDB ID 1f16) and activated BAX (PDB ID 2k7w). The
            activation causes a charge redistribution that also includes C
            domain depolarization. This depolarization causes release of the C
            domain, which can then penetrate mitochondrial membrane and start
            the apoptosis as described in the literature.
          </p>
        </Example>
        <Example
          title="Transmembrane protein"
          image={{ src: Receptor, alt: "Receptor" }}
          actions={[{ name: "Receptor", action: () => {} }]}
        >
          <p>
            The nicotinic acetylcholine receptor passes the cell membrane (see
            the figure, part A) and serves as an ion channel (more details). We
            obtained its structure from Protein Data Bank Europe (PDB ID 2bg9),
            added missing hydrogens via WHAT IF and calculated the partial
            atomic charges using ACC II with default settings. Visualization of
            partial charges on the surface highlights the difference between
            nonpolar transmembrane part (mostly white due to charge around zero)
            and polar surface of extracellular and cytoplasmic parts (with
            mosaic of blue positive and red negative charges). The comparison
            demonstrates that this charge distribution agrees with receptor
            membrane position reported in literature.
          </p>
        </Example>
      </div>
    </Section>
  );
};
