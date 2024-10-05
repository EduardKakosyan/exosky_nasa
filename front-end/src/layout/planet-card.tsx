import { Planet } from "../components/Planet";

type Props = {
   imgSrc: string;
}

export function PlanetCard({ imgSrc }: Props) {
   return (
      <Planet imgSrc={imgSrc}/>
   );
}