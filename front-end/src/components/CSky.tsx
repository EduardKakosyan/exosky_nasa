import { useRef, useEffect } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export function CSky() {
   const imageSrc: string = 'sky_image.png';
   const mountRef = useRef<HTMLDivElement>(null);
   const controlsRef = useRef<OrbitControls | null>(null);
   const isDrawing = useRef(false);

   const initializeScene = () => {
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

      camera.position.set(150, 0, 40);

      const controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.5;
      controls.enableZoom = true;
      controls.zoomSpeed = 2;

      controls.mouseButtons.RIGHT = null;

      controls.minDistance = 50;
      controls.maxDistance = 500;

      controls.minAzimuthAngle = 0;          // -90 degrees
      controls.maxAzimuthAngle = -Math.PI;   // 90 degrees
      controls.minPolarAngle = 0;            // 0 degrees
      controls.maxPolarAngle = Math.PI;      // 180 degrees

      controlsRef.current = controls; // Store the controls reference

      const drawOnSphere = (event: MouseEvent) => {
         if (!isDrawing.current) return;

         const mouse = new THREE.Vector2(
            (event.clientX / mount.clientWidth) * 2 - 1,
            -(event.clientY / mount.clientHeight) * 2 + 1
         );

         const raycaster = new THREE.Raycaster();
         raycaster.setFromCamera(mouse, camera);

         const intersects = raycaster.intersectObject(sphere);
         if (intersects.length > 0) {
            const intersect = intersects[0];
            const point = intersect.point;

            const dotGeometry = new THREE.SphereGeometry(5, 32, 32);
            const dotMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
            const dot = new THREE.Mesh(dotGeometry, dotMaterial);
            dot.position.copy(point);
            scene.add(dot);
         }
      };

      const onMouseDown = (event: MouseEvent) => {
         if (event.button === 2) { // Right mouse button
            isDrawing.current = true;
         }
      };

      const onMouseUp = (event: MouseEvent) => {
         if (event.button === 2) { // Right mouse button
            isDrawing.current = false;
         }
      };

      mount.addEventListener('mousedown', onMouseDown);
      mount.addEventListener('mousemove', drawOnSphere);
      mount.addEventListener('mouseup', onMouseUp);

      const animate = () => {
         requestAnimationFrame(animate);
         renderer.render(scene, camera);
      };

      animate();
   };

   useEffect(() => {
      initializeScene();
   }, []);


   return <div ref={mountRef} style={{ width: '100%', height: '100vh' }} />;
}
