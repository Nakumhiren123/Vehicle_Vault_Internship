import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/**
 * VehicleVault — 360° Car Viewer
 * Usage: initCarViewer('container-id', '/media/car_models/car.glb', { options })
 */
export function initCarViewer(containerId, modelUrl, options = {}) {
  const container = document.getElementById(containerId);
  if (!container || !modelUrl) return;

  const width  = container.clientWidth  || 600;
  const height = container.clientHeight || 420;

  // ── Renderer ──────────────────────────────────────────────
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  container.style.position = 'relative';
  container.appendChild(renderer.domElement);

  // ── Scene ─────────────────────────────────────────────────
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(options.bgColor ?? 0x111827);

  // Optional subtle gradient fog for depth
  scene.fog = new THREE.Fog(options.bgColor ?? 0x111827, 12, 25);

  // ── Camera ────────────────────────────────────────────────
  const camera = new THREE.PerspectiveCamera(38, width / height, 0.1, 100);
  camera.position.set(4, 2, 5);

  // ── Lights ────────────────────────────────────────────────
  scene.add(new THREE.AmbientLight(0xffffff, 0.6));

  const key = new THREE.DirectionalLight(0xffffff, 2.5);
  key.position.set(6, 10, 6);
  key.castShadow = true;
  key.shadow.camera.near = 0.5;
  key.shadow.camera.far  = 30;
  key.shadow.mapSize.set(1024, 1024);
  scene.add(key);

  const fill = new THREE.DirectionalLight(0x8ea8ff, 1.0);
  fill.position.set(-6, 3, -4);
  scene.add(fill);

  const rim = new THREE.DirectionalLight(0xffffff, 1.8);
  rim.position.set(0, 6, -8);
  scene.add(rim);

  // ── Ground (reflective showroom floor) ────────────────────
  const ground = new THREE.Mesh(
    new THREE.CircleGeometry(5, 64),
    new THREE.MeshStandardMaterial({
      color: 0x1a1a2e,
      roughness: 0.15,
      metalness: 0.6,
    })
  );
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);

  // ── Orbit Controls (360° rotation) ───────────────────────
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping    = true;
  controls.dampingFactor    = 0.06;
  controls.minDistance      = 2.5;
  controls.maxDistance      = 11;
  controls.maxPolarAngle    = Math.PI / 2.05;
  controls.autoRotate       = options.autoRotate ?? true;
  controls.autoRotateSpeed  = options.rotateSpeed ?? 1.8;
  controls.target.set(0, 0.5, 0);

  // Pause auto-rotate on interaction, resume after 3s
  renderer.domElement.addEventListener('pointerdown', () => {
    controls.autoRotate = false;
  });
  renderer.domElement.addEventListener('pointerup', () => {
    setTimeout(() => { controls.autoRotate = true; }, 3000);
  });

  // ── Loading Overlay ───────────────────────────────────────
  const overlay = document.createElement('div');
  overlay.style.cssText = `
    position:absolute; inset:0; display:flex; flex-direction:column;
    align-items:center; justify-content:center; background:rgba(0,0,0,0.45);
    border-radius:inherit; z-index:10;
  `;
  overlay.innerHTML = `
    <style>
      @keyframes vv-spin { to { transform:rotate(360deg); } }
      .vv-spin-ring {
        width:44px; height:44px;
        border:3px solid rgba(255,255,255,0.15);
        border-top-color:#e63946;
        border-radius:50%;
        animation:vv-spin .9s linear infinite;
      }
      .vv-spin-label {
        margin-top:12px; color:#ccc;
        font:13px/1 'Segoe UI',sans-serif; letter-spacing:.5px;
      }
    </style>
    <div class="vv-spin-ring"></div>
    <div class="vv-spin-label" id="${containerId}-pct">Loading 3D Model…</div>
  `;
  container.appendChild(overlay);

  // ── Hint Bar ─────────────────────────────────────────────
  const hint = document.createElement('div');
  hint.style.cssText = `
    position:absolute; bottom:10px; left:0; right:0; text-align:center;
    font:12px 'Segoe UI',sans-serif; color:rgba(255,255,255,0.35);
    pointer-events:none; display:none;
  `;
  hint.textContent = '🖱 Drag to rotate  •  Scroll to zoom';
  container.appendChild(hint);

  // ── Load Model ───────────────────────────────────────────
  const loader = new GLTFLoader();
  loader.load(
    modelUrl,
    (gltf) => {
      overlay.remove();
      hint.style.display = 'block';

      const model = gltf.scene;

      // Auto-center & scale to fit ~3 units
      const box    = new THREE.Box3().setFromObject(model);
      const center = box.getCenter(new THREE.Vector3());
      const size   = box.getSize(new THREE.Vector3());
      const scale  = 3 / Math.max(size.x, size.y, size.z);

      model.scale.setScalar(scale);
      model.position.sub(center.multiplyScalar(scale));
      model.position.y = 0;

      model.traverse((child) => {
        if (child.isMesh) {
          child.castShadow    = true;
          child.receiveShadow = true;
        }
      });

      scene.add(model);
    },
    (xhr) => {
      if (xhr.total) {
        const pct = Math.round((xhr.loaded / xhr.total) * 100);
        const el  = document.getElementById(`${containerId}-pct`);
        if (el) el.textContent = `Loading… ${pct}%`;
      }
    },
    (err) => {
      overlay.innerHTML = `
        <div style="color:#e63946;font:14px 'Segoe UI',sans-serif;text-align:center;padding:20px;">
          ⚠ Failed to load 3D model<br>
          <span style="font-size:12px;color:#888;">Check the .glb file path</span>
        </div>`;
      console.error('[VehicleVault 3D Viewer]', err);
    }
  );

  // ── Resize Handler ───────────────────────────────────────
  const onResize = () => {
    const w = container.clientWidth;
    const h = container.clientHeight || 420;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  };
  window.addEventListener('resize', onResize);

  // ── Animate ──────────────────────────────────────────────
  let rafId;
  function animate() {
    rafId = requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  }
  animate();

  // Return controls for external use (e.g. destroy)
  return {
    scene, camera, controls, renderer,
    destroy() {
      cancelAnimationFrame(rafId);
      window.removeEventListener('resize', onResize);
      renderer.dispose();
    }
  };
}