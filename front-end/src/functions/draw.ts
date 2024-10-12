import * as THREE from 'three';

// Function to create a dot
export function createDot(position: THREE.Vector3, scene: THREE.Scene, pointsRef: React.MutableRefObject<THREE.Mesh[]>) {
   const dotGeometry = new THREE.SphereGeometry(1, 32, 32);
   const dotMaterial = new THREE.MeshBasicMaterial({ color: 'white' });
   const dot = new THREE.Mesh(dotGeometry, dotMaterial);
   dot.position.copy(position);
   scene.add(dot);
   pointsRef.current.push(dot);
};

// Function to create a line between two dots
export function createLine(start: THREE.Vector3, end: THREE.Vector3, scene: THREE.Scene, linesRef: React.MutableRefObject<THREE.Line[]>) {
   const material = new THREE.LineBasicMaterial({ color: 'white' });
   const points = [start, end];
   const geometry = new THREE.BufferGeometry().setFromPoints(points);
   const line = new THREE.Line(geometry, material);
   scene.add(line);
   linesRef.current.push(line);
};

// Function to reset the canvas
export function resetCanvas(
      pointsRef: React.MutableRefObject<THREE.Mesh[]>, 
      linesRef: React.MutableRefObject<THREE.Line[]>, 
      scene: THREE.Scene
   ) 
   {
      pointsRef.current.forEach(dot => scene.remove(dot)); // Remove all dots
      pointsRef.current = []; // Clear dots reference
      linesRef.current.forEach(line => scene.remove(line)); // Remove all lines
      linesRef.current = []; // Clear lines reference
};
