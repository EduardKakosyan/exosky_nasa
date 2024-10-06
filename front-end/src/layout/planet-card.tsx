import { Planet } from "../components/Planet";

type Props = {
   imgSrc: string;
   planetName: string;
}

export function PlanetCard({ imgSrc, planetName }: Props) {
   return (
      <div className="border border-gray-700 rounded-2xl bg-gray-500 bg-opacity-20 flex flex-row z-20 w-[400px] h-[180px] items-center">
         <div>
            <Planet imgSrc={imgSrc} />
         </div>
         <div className="text-white pl-8">
            <span className="font-bold text-3xl">{planetName}</span>
            <p className="mt-2 mb-5">{planetName}</p>
            <button className="px-4 py-2 rounded-md border border-neutral-300 bg-neutral-100 text-neutral-900 text-md font-semibold hover:-translate-y-1 transform transition duration-200 hover:shadow-md">
               View Sky
            </button>
         </div>
      </div>

   );
}