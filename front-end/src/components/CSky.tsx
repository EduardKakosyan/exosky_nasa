import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { FontLoader } from 'three/examples/jsm/loaders/FontLoader.js';
import { TextGeometry } from 'three/examples/jsm/geometries/TextGeometry.js';

export function CSky() {
   const imageSrc: string = 'sky_image.png';
   const mountRef = useRef<HTMLDivElement>(null);
   const [camera, setCamera] = useState<THREE.PerspectiveCamera | null>(null);
   const [controls, setControls] = useState<OrbitControls | null>(null);
   const scene = new THREE.Scene();
   const planetXTextMeshRef = useRef<THREE.Mesh | null>(null);
   const planetYTextMeshRef = useRef<THREE.Mesh | null>(null);

   useEffect(() => {
      // Set up camera and renderer
      const mount = mountRef.current!;
      const camera = new THREE.PerspectiveCamera(75, mount.clientWidth / mount.clientHeight, 0.1, 2000);
      const renderer = new THREE.WebGLRenderer();
      renderer.setSize(mount.clientWidth, mount.clientHeight);
      mount.appendChild(renderer.domElement);

      // Create sky background
      const geometry = new THREE.SphereGeometry(500, 64, 32);
      geometry.scale(-1, 1, 1);
      const texture = new THREE.TextureLoader().load(imageSrc);
      const material = new THREE.MeshBasicMaterial({ map: texture });
      const sphere = new THREE.Mesh(geometry, material);
      scene.add(sphere);

      // Create two planets (PlanetX and PlanetY)
      const planetGeometry = new THREE.SphereGeometry(10, 10, 10);
      const planetXMaterial = new THREE.MeshBasicMaterial({ color: 'red' });
      const planetYMaterial = new THREE.MeshBasicMaterial({ color: 'blue' });

      const planetX = new THREE.Mesh(planetGeometry, planetXMaterial);
      const planetY = new THREE.Mesh(planetGeometry, planetYMaterial);

      //.position.set(front/back, up/down, left/right);
      planetX.position.set(-470, 0, -50);
      planetY.position.set(-450, 50, 150);

      scene.add(planetX);
      scene.add(planetY);

      // Set camera position
      camera.position.set(150, 0, 40);

      // Set up OrbitControls
      const controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.5;
      controls.enableZoom = true;
      controls.zoomSpeed = 2;
      controls.minDistance = 1;
      controls.maxDistance = 500;

      setCamera(camera);
      setControls(controls);

      const raycaster = new THREE.Raycaster();
      const mouse = new THREE.Vector2();

      // Create text mesh for PlanetX and PlanetY, but initially invisible
      const createTextMesh = (text: string, position: THREE.Vector3, ref: React.MutableRefObject<THREE.Mesh | null>) => {
         const loader = new FontLoader();
         loader.load('/myFont.json', (font) => {
            const textGeometry = new TextGeometry(text, {
               font: font,
               size: 10,
               height: 1,
               curveSegments: 12,
               bevelEnabled: false,
            });
            const textMaterial = new THREE.MeshBasicMaterial({ color: 'white' });
            const textMesh = new THREE.Mesh(textGeometry, textMaterial);

            textMesh.position.copy(position);
            textMesh.rotateY(20);
            scene.add(textMesh);

            textMesh.visible = false;  // Initially make it invisible
            ref.current = textMesh;
         });
      };

      createTextMesh("Planet X", new THREE.Vector3(-470, 0, -60), planetXTextMeshRef); // Create text mesh for Planet X
      createTextMesh("Planet Y", new THREE.Vector3(-450, 50, 140), planetYTextMeshRef); // Create text mesh for Planet Y

      // Handle mouse hover
      const handleHover = (event: MouseEvent) => {
         mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
         mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

         raycaster.setFromCamera(mouse, camera!);
         const intersects = raycaster.intersectObjects([planetX, planetY]);

         if (intersects.length > 0) {
            const intersectedObject = intersects[0].object;

            // Show or hide the appropriate text mesh based on the planet being hovered
            if (intersectedObject === planetX && planetXTextMeshRef.current) {
               planetXTextMeshRef.current.visible = true;
               if (planetYTextMeshRef.current) planetYTextMeshRef.current.visible = false;
            } else if (intersectedObject === planetY && planetYTextMeshRef.current) {
               planetYTextMeshRef.current.visible = true;
               if (planetXTextMeshRef.current) planetXTextMeshRef.current.visible = false;
            }
         } else {
            // Hide both texts when no planet is hovered
            if (planetXTextMeshRef.current) planetXTextMeshRef.current.visible = false;
            if (planetYTextMeshRef.current) planetYTextMeshRef.current.visible = false;
         }
      };

      window.addEventListener('mousemove', handleHover);

      // Handle mouse clicks (for color change)
      const handleClick = (event: MouseEvent) => {
         mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
         mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

         raycaster.setFromCamera(mouse, camera!);
         const intersects = raycaster.intersectObjects([planetX, planetY]);

         if (intersects.length > 0) {
            const intersectedObject = intersects[0].object;
            if (intersectedObject === planetX) {
               console.log('Planet X clicked!');
               planetX.material.color.set('yellow');
            } else if (intersectedObject === planetY) {
               console.log('Planet Y clicked!');
               planetY.material.color.set('yellow');
            }
         }
      };

      window.addEventListener('click', handleClick);

      // Animation loop
      const animate = () => {
         requestAnimationFrame(animate);
         controls.update();

         // Make the text always face the camera (billboard effect)
         if (planetXTextMeshRef.current) {
            planetXTextMeshRef.current.lookAt(camera!.position);
         }
         if (planetYTextMeshRef.current) {
            planetYTextMeshRef.current.lookAt(camera!.position);
         }
         
         renderer.render(scene, camera);
      };

      animate();

      return () => {
         window.removeEventListener('mousemove', handleHover);
         window.removeEventListener('click', handleClick);
         mount.removeChild(renderer.domElement);
      };
   }, []);

   return <div ref={mountRef} style={{ width: '100%', height: '100vh' }} />;
}
