import BannerImage from "@acc2/assets/images/1RLB.png";

export const Banner = () => {
  return (
    <div className="w-11/12 md:w-4/5 max-w-content mx-auto">
      <div className="flex relative max-w-[750px] mx-auto">
        <div className="my-16 p-2 bg-black bg-opacity-10 w-fit z-30">
          <h1 className="font-muni font-bold text-primary text-4xl md:text-6xl">
            <span className="block bg-white w-fit">Atomic</span>
            <span className="block my-2 bg-white w-fit">Charge</span>
            <span className="block bg-white w-fit">Calculator II</span>
          </h1>
        </div>
        <img
          src={BannerImage}
          alt="1RLB"
          className="absolute min-w-[350px] sm:right-0"
          width={500}
          height={250}
        />
      </div>
    </div>
  );
};
