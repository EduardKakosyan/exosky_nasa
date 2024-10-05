import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export function Sky() {
   const imageSrc: string = '../../public/sky_image.png';
   const mountRef = useRef<HTMLDivElement>(null);
   const [isDrawing, setIsDrawing] = useState(false);
   const [camera, setCamera] = useState<THREE.PerspectiveCamera | null>(null);
   const [controls, setControls] = useState<OrbitControls | null>(null);

   useEffect(() => {
      const mount = mountRef.current!;
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(75, mount.clientWidth / mount.clientHeight, 0.1, 2000);
      const renderer = new THREE.WebGLRenderer();
      renderer.setSize(mount.clientWidth, mount.clientHeight);
      mount.appendChild(renderer.domElement);

      const geometry = new THREE.SphereGeometry(500, 64, 32);
      geometry.scale(-1, 1, 1);

      const texture = new THREE.TextureLoader().load(imageSrc);
      const material = new THREE.MeshBasicMaterial({ map: texture });
      const sphere = new THREE.Mesh(geometry, material);
      scene.add(sphere);

      // camera.position.set(0.5, -0.025, 0.1);
      camera.position.set(150, 0, 40)

      const controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.5;
      controls.enableZoom = true;
      controls.zoomSpeed = 2;

      controls.minDistance = 50;
      controls.maxDistance = 500;

      // Limit the orbit controls
      controls.minAzimuthAngle = 0;          // -90 degrees
      controls.maxAzimuthAngle = -Math.PI;   // 90 degrees
      controls.minPolarAngle = 0;            // 0 degrees
      controls.maxPolarAngle = Math.PI;      // 180 degrees

      setCamera(camera);
      setControls(controls);

      const animate = () => {
         requestAnimationFrame(animate);
         controls.update();
         renderer.render(scene, camera);
      };

      animate();

      const handleKeyDown = (event: KeyboardEvent) => {
         if (event.key === 'D' || event.key === 'd') {
            setIsDrawing(true);
         } 
         
         else if (event.key === 'V' || event.key === 'v') {
            setIsDrawing(false);
         }
      };

      const handleMouseMove = (event: MouseEvent) => {
         if (isDrawing) {
            controls.enabled = false;

            // Implement drawing logic here
            const canvas = document.createElement('canvas');
            canvas.width = texture.image.width;
            canvas.height = texture.image.height;
            const context = canvas.getContext('2d');
            context?.drawImage(texture.image, 0, 0);

            // Example drawing: draw a red dot at the mouse position
            if (context) {
               context.fillStyle = 'red';
            }
            context?.beginPath();
            context?.arc(event.clientX, event.clientY, 5, 0, Math.PI * 2);
            context?.fill();

            texture.image = canvas;
            texture.needsUpdate = true;
         }
      };

      window.addEventListener('keydown', handleKeyDown);
      window.addEventListener('mousemove', handleMouseMove);

      return () => {
         window.removeEventListener('keydown', handleKeyDown);
         window.removeEventListener('mousemove', handleMouseMove);
         mount.removeChild(renderer.domElement);
      };
   }, [isDrawing]);

   return <div ref={mountRef} style={{ width: '100%', height: '100vh' }} />;
};
 