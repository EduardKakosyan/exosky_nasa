import { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Mesh } from 'three';
import { useTexture } from '@react-three/drei';

type Props = {
   imgSrc: string;
}

function RotatingSphere({ imgSrc }: Props) {
   const sphereRef = useRef<Mesh>(null);
   const texture = useTexture(imgSrc);

   useFrame(() => {
      if (sphereRef.current) {
         sphereRef.current.rotation.y += 0.005;
      }
   });

   return (
      <mesh ref={sphereRef}>
         <sphereGeometry args={[2.5, 32, 32]} />
         <meshStandardMaterial map={texture} />
      </mesh>
   );
}

export function Planet({ imgSrc }: Props) {
   return (
      <div className='w-[180px]'>
         <Canvas>
            <ambientLight intensity={6}/>
            <pointLight position={[0, 0, 10]} intensity={20}/>
            <RotatingSphere imgSrc={imgSrc} />
         </Canvas>
      </div>
      
   );
}