/**
 * Road Health Intelligence (RHI) - Rich 3D Smart City & Road Infrastructure Scene
 * Powered by Three.js (WebGL)
 * Visual Style: Premium Light Enterprise Smart City (#F5F7FA, Navy #0F172A, Teal #0F766E, Blue #2563EB)
 * Features:
 *  - Prominent multi-lane asphalt highways & flyover overpasses
 *  - Color-coded road health segments (Green #16A34A, Amber #F59E0B, Red #DC2626)
 *  - Realistic 3D Road Roller & Maintenance Fleet Vehicles with rotating wheels & amber beacons
 *  - 3D CCTV AI Surveillance Towers with scanning cones
 *  - 3D Overhead Highway Gantry & Warning Signs
 *  - High-visibility Traffic Safety Cones & Barricades
 *  - Animated 3D Floating GPS Teardrop Pins with pulse wave rings
 *  - Low-poly Roadside Greenery Trees and Smart City Glass Architecture
 */

window.RHIScene = (function () {
  let scene, camera, renderer;
  let heroContainer, dashContainer;
  let roads = [];
  let trafficPoints = [];
  let maintenanceVehicles = [];
  let buildingMeshes = [];
  let gpsPins = [];
  let cctvTowers = [];
  let scanningCones = [];
  let raycaster, mouse;
  let currentViewMode = "hero"; // 'hero' or 'dashboard'
  let animationFrameId;
  let clock = 0;

  // Rich multi-segment road network curves
  const ROAD_DEFINITIONS = [
    {
      code: "RHI-2048",
      name: "Ring Road Expressway - Sector 4",
      health: 54,
      status: "CRITICAL",
      color: 0xDC2626, // Clean Coral Red
      width: 7.5,
      curve: [
        [-160, 2, -70],
        [-80, 5, -30],
        [0, 8, 0],
        [80, 5, 40],
        [160, 2, 90]
      ]
    },
    {
      code: "RHI-1042",
      name: "Cyber Hub North Corridor",
      health: 92,
      status: "HEALTHY",
      color: 0x16A34A, // Clean Emerald Green
      width: 7.5,
      curve: [
        [-130, 2, 90],
        [-50, 3, 65],
        [25, 4, 35],
        [95, 3, -30],
        [150, 2, -110]
      ]
    },
    {
      code: "RHI-3091",
      name: "Metro Outer Bypass - Zone B",
      health: 64,
      status: "HIGH",
      color: 0xF59E0B, // Clean Amber
      width: 6.5,
      curve: [
        [-170, 1, 15],
        [-90, 4, 30],
        [0, 2, -60],
        [100, 4, -45],
        [180, 1, -25]
      ]
    },
    {
      code: "RHI-5012",
      name: "Airport Elevated Flyover Link",
      health: 88,
      status: "HEALTHY",
      color: 0x2563EB, // Secondary Blue
      width: 6.5,
      curve: [
        [-70, 10, -140],
        [0, 14, -70],
        [45, 16, 0],
        [85, 10, 80],
        [120, 4, 150]
      ]
    },
    {
      code: "RHI-4120",
      name: "Industrial Tech Corridor South",
      health: 50,
      status: "CRITICAL",
      color: 0xDC2626, // Clean Coral Red
      width: 6.0,
      curve: [
        [-95, 1, -120],
        [-80, 2, -45],
        [-70, 2, 45],
        [-55, 1, 130]
      ]
    }
  ];

  function init(heroDomId, dashDomId) {
    heroContainer = document.getElementById(heroDomId);
    dashContainer = document.getElementById(dashDomId);

    const targetContainer = heroContainer || dashContainer;
    if (!targetContainer || typeof THREE === "undefined") {
      console.warn("[RHI 3D] Three.js container or library not ready yet.");
      return;
    }

    const width = targetContainer.clientWidth || window.innerWidth;
    const height = targetContainer.clientHeight || window.innerHeight;

    // 1. Scene setup with clean light background #F5F7FA
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xF5F7FA);
    scene.fog = new THREE.FogExp2(0xF5F7FA, 0.0022);

    // 2. Camera setup
    camera = new THREE.PerspectiveCamera(46, width / height, 1, 2500);
    setCameraForHero();

    // 3. WebGL Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.1;

    targetContainer.appendChild(renderer.domElement);

    // 4. Clean Daylight & Studio Lighting
    const ambientLight = new THREE.AmbientLight(0xFFFFFF, 2.5);
    scene.add(ambientLight);

    const hemiLight = new THREE.HemisphereLight(0xF8FAFC, 0xE2E8F0, 1.2);
    hemiLight.position.set(0, 200, 0);
    scene.add(hemiLight);

    const sunLight = new THREE.DirectionalLight(0xFFFFFF, 1.6);
    sunLight.position.set(120, 220, 100);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.width = 2048;
    sunLight.shadow.mapSize.height = 2048;
    scene.add(sunLight);

    const softTealLight = new THREE.PointLight(0x0F766E, 1.2, 500);
    softTealLight.position.set(0, 80, 0);
    scene.add(softTealLight);

    // 5. Build Environment & Infrastructure Models
    createGroundTerrain();
    createModernCityBuildings();
    createHighwayNetwork();
    createRoadMaintenanceVehicles();
    createSurveillanceCCTVTowers();
    createHighwayOverheadGantries();
    createTrafficSafetyCones();
    createGPSLocationPins();
    createRoadsideForestry();
    createTrafficFlowParticles();

    // 6. Interaction & Raycasting
    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();

    window.addEventListener("resize", onWindowResize);
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("click", onCanvasClick);

    animate();
    console.log("[RHI 3D] Full 3D Road Infrastructure scene loaded successfully.");
  }

  function createGroundTerrain() {
    // 1. Light grey precision grid
    const gridHelper = new THREE.GridHelper(900, 90, 0xCBD5E1, 0xE2E8F0);
    gridHelper.position.y = -0.4;
    scene.add(gridHelper);

    // 2. Crisp terrain base disc
    const geo = new THREE.CircleGeometry(480, 64);
    const mat = new THREE.MeshStandardMaterial({
      color: 0xF8FAFC,
      roughness: 0.95,
      metalness: 0.05
    });
    const disc = new THREE.Mesh(geo, mat);
    disc.rotation.x = -Math.PI / 2;
    disc.position.y = -0.8;
    disc.receiveShadow = true;
    scene.add(disc);

    // 3. Green parkland zones
    const parkLocations = [
      { x: -110, z: -10, r: 45 },
      { x: 110, z: -10, r: 50 },
      { x: 20, z: 90, r: 40 },
      { x: -50, z: 120, r: 35 }
    ];

    parkLocations.forEach(p => {
      const pGeo = new THREE.CircleGeometry(p.r, 32);
      const pMat = new THREE.MeshBasicMaterial({ color: 0xDCFCE7 });
      const park = new THREE.Mesh(pGeo, pMat);
      park.rotation.x = -Math.PI / 2;
      park.position.set(p.x, -0.6, p.z);
      scene.add(park);
    });
  }

  function createModernCityBuildings() {
    const bldgGeo = new THREE.BoxGeometry(1, 1, 1);
    const bldgMatSlate = new THREE.MeshStandardMaterial({ color: 0xE2E8F0, roughness: 0.85, metalness: 0.1 });
    const bldgMatNavy = new THREE.MeshStandardMaterial({ color: 0xCBD5E1, roughness: 0.7, metalness: 0.2 });
    const bldgMatGlass = new THREE.MeshStandardMaterial({ color: 0xBAE6FD, roughness: 0.2, metalness: 0.6, transparent: true, opacity: 0.85 });

    const materials = [bldgMatSlate, bldgMatNavy, bldgMatGlass];

    for (let i = 0; i < 85; i++) {
      const w = 14 + Math.random() * 22;
      const d = 14 + Math.random() * 22;
      const h = 25 + Math.random() * 95;

      const posX = (Math.random() - 0.5) * 650;
      const posZ = (Math.random() - 0.5) * 650;

      // Keep center stage and roadway corridors open
      if (Math.sqrt(posX * posX + posZ * posZ) < 100) continue;

      const mat = materials[Math.floor(Math.random() * materials.length)];
      const bldg = new THREE.Mesh(bldgGeo, mat);
      bldg.scale.set(w, h, d);
      bldg.position.set(posX, h / 2, posZ);
      bldg.castShadow = true;
      bldg.receiveShadow = true;
      scene.add(bldg);
      buildingMeshes.push(bldg);
    }
  }

  function createHighwayNetwork() {
    ROAD_DEFINITIONS.forEach((def) => {
      const points = def.curve.map((p) => new THREE.Vector3(p[0], p[1], p[2]));
      const curve = new THREE.CatmullRomCurve3(points);
      
      // 1. Asphalt Road Bed (Wide multi-lane roadway)
      const roadBedGeo = new THREE.TubeGeometry(curve, 72, def.width / 2, 8, false);
      const roadBedMat = new THREE.MeshStandardMaterial({
        color: 0x334155, // Clean dark slate asphalt
        roughness: 0.85,
        metalness: 0.1
      });
      const roadMesh = new THREE.Mesh(roadBedGeo, roadBedMat);
      roadMesh.userData = { roadCode: def.code, roadName: def.name, health: def.health, status: def.status };
      roadMesh.receiveShadow = true;
      scene.add(roadMesh);
      roads.push({ mesh: roadMesh, curve: curve, def: def });

      // 2. Road Health Glowing Edge Line (Green / Amber / Red)
      const glowMat = new THREE.MeshBasicMaterial({
        color: def.color,
        transparent: true,
        opacity: 0.95
      });
      const glowGeo = new THREE.TubeGeometry(curve, 72, (def.width / 2) + 0.35, 4, false);
      const glowMesh = new THREE.Mesh(glowGeo, glowMat);
      scene.add(glowMesh);

      // 3. Flyover Support Pillars for elevated highways
      for (let i = 1; i < points.length - 1; i++) {
        const pt = points[i];
        if (pt.y > 3) {
          const pillarGeo = new THREE.CylinderGeometry(1.2, 1.4, pt.y, 12);
          const pillarMat = new THREE.MeshStandardMaterial({ color: 0x94A3B8, roughness: 0.8 });
          const pillar = new THREE.Mesh(pillarGeo, pillarMat);
          pillar.position.set(pt.x, pt.y / 2, pt.z);
          pillar.castShadow = true;
          scene.add(pillar);
        }
      }
    });
  }

  /**
   * 3D Road Roller & Maintenance Fleet Patrol Vehicles
   */
  function createRoadMaintenanceVehicles() {
    // 1. Detailed Heavy Asphalt Road Roller on Ring Road Sector 4
    const rollerGroup = new THREE.Group();
    
    // Roller Frame
    const frameGeo = new THREE.BoxGeometry(4.2, 1.8, 7.5);
    const frameMat = new THREE.MeshStandardMaterial({ color: 0xF59E0B, metalness: 0.4, roughness: 0.5 }); // Safety Yellow
    const frame = new THREE.Mesh(frameGeo, frameMat);
    frame.position.y = 1.6;
    frame.castShadow = true;
    rollerGroup.add(frame);

    // Front Giant Compactor Steel Drum
    const drumGeo = new THREE.CylinderGeometry(1.8, 1.8, 4.4, 24);
    const drumMat = new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.8, roughness: 0.2 }); // Polished Steel
    const drum = new THREE.Mesh(drumGeo, drumMat);
    drum.rotation.z = Math.PI / 2;
    drum.position.set(0, 1.8, 3.2);
    drum.castShadow = true;
    rollerGroup.add(drum);

    // Operator Glass Cabin
    const cabGeo = new THREE.BoxGeometry(3.2, 2.2, 2.8);
    const cabMat = new THREE.MeshStandardMaterial({ color: 0x0F172A, metalness: 0.2, roughness: 0.1, transparent: true, opacity: 0.8 });
    const cab = new THREE.Mesh(cabGeo, cabMat);
    cab.position.set(0, 3.2, -0.6);
    rollerGroup.add(cab);

    // Flashing Amber Beacon on Roof
    const beaconGeo = new THREE.CylinderGeometry(0.35, 0.35, 0.6, 12);
    const beaconMat = new THREE.MeshBasicMaterial({ color: 0xF59E0B });
    const beacon = new THREE.Mesh(beaconGeo, beaconMat);
    beacon.position.set(0, 4.6, -0.6);
    rollerGroup.add(beacon);

    rollerGroup.position.set(-10, 6, 8);
    rollerGroup.scale.set(0.7, 0.7, 0.7);
    scene.add(rollerGroup);

    // 2. Active AI Patrol Fleet Vehicles traversing routes
    roads.forEach((r, idx) => {
      const truckGroup = new THREE.Group();

      // Truck Body
      const bodyMat = new THREE.MeshStandardMaterial({
        color: idx % 2 === 0 ? 0x0F766E : 0x2563EB, // Teal or Blue
        metalness: 0.3,
        roughness: 0.4
      });
      const body = new THREE.Mesh(new THREE.BoxGeometry(2.8, 1.4, 5.0), bodyMat);
      body.position.y = 1.0;
      body.castShadow = true;
      truckGroup.add(body);

      // Cabin Glass
      const windshield = new THREE.Mesh(
        new THREE.BoxGeometry(2.4, 1.1, 2.0),
        new THREE.MeshStandardMaterial({ color: 0x0F172A, roughness: 0.1 })
      );
      windshield.position.set(0, 1.9, 0.8);
      truckGroup.add(windshield);

      // Roof Beacon
      const bLight = new THREE.Mesh(
        new THREE.SphereGeometry(0.3, 8, 8),
        new THREE.MeshBasicMaterial({ color: 0xF59E0B })
      );
      bLight.position.set(0, 2.6, 0.8);
      truckGroup.add(bLight);

      // 4 Wheels
      const wheelMat = new THREE.MeshStandardMaterial({ color: 0x1E293B, roughness: 0.9 });
      const wheelGeo = new THREE.CylinderGeometry(0.55, 0.55, 0.5, 12);
      const w1 = new THREE.Mesh(wheelGeo, wheelMat);
      w1.rotation.z = Math.PI / 2;
      w1.position.set(-1.45, 0.55, 1.5);
      const w2 = new THREE.Mesh(wheelGeo, wheelMat);
      w2.rotation.z = Math.PI / 2;
      w2.position.set(1.45, 0.55, 1.5);
      const w3 = new THREE.Mesh(wheelGeo, wheelMat);
      w3.rotation.z = Math.PI / 2;
      w3.position.set(-1.45, 0.55, -1.5);
      const w4 = new THREE.Mesh(wheelGeo, wheelMat);
      w4.rotation.z = Math.PI / 2;
      w4.position.set(1.45, 0.55, -1.5);
      truckGroup.add(w1, w2, w3, w4);

      truckGroup.scale.set(0.65, 0.65, 0.65);
      scene.add(truckGroup);

      maintenanceVehicles.push({
        group: truckGroup,
        curve: r.curve,
        progress: (idx * 0.28) % 1.0,
        speed: 0.0011 + (idx * 0.0003)
      });
    });
  }

  /**
   * 3D AI CCTV Surveillance Towers with Scanning Cones
   */
  function createSurveillanceCCTVTowers() {
    const cctvPositions = [
      { x: -50, y: 0, z: 20, rot: 0.4 },
      { x: 50, y: 0, z: -20, rot: -0.7 },
      { x: -15, y: 0, z: -75, rot: 1.1 },
      { x: 90, y: 0, z: 60, rot: -2.1 }
    ];

    cctvPositions.forEach(pos => {
      const towerGroup = new THREE.Group();

      // Steel Mast
      const poleGeo = new THREE.CylinderGeometry(0.4, 0.6, 18, 12);
      const poleMat = new THREE.MeshStandardMaterial({ color: 0x64748B, metalness: 0.7, roughness: 0.3 });
      const pole = new THREE.Mesh(poleGeo, poleMat);
      pole.position.y = 9;
      pole.castShadow = true;
      towerGroup.add(pole);

      // Solar Panel on Top
      const solarGeo = new THREE.BoxGeometry(3.5, 0.15, 2.2);
      const solarMat = new THREE.MeshStandardMaterial({ color: 0x1E3A8A, metalness: 0.8, roughness: 0.2 });
      const solar = new THREE.Mesh(solarGeo, solarMat);
      solar.rotation.x = 0.4;
      solar.position.set(0, 18.5, 0);
      towerGroup.add(solar);

      // Camera Mount Arm & Camera Box
      const arm = new THREE.Mesh(new THREE.BoxGeometry(3.4, 0.4, 0.4), poleMat);
      arm.position.set(1.7, 16.5, 0);
      towerGroup.add(arm);

      const camBody = new THREE.Mesh(
        new THREE.BoxGeometry(2.0, 1.2, 1.2),
        new THREE.MeshStandardMaterial({ color: 0x0F172A, metalness: 0.5, roughness: 0.2 })
      );
      camBody.position.set(3.2, 16.0, 0);
      towerGroup.add(camBody);

      // Teal LED Status Sensor
      const lens = new THREE.Mesh(
        new THREE.SphereGeometry(0.35, 8, 8),
        new THREE.MeshBasicMaterial({ color: 0x0F766E })
      );
      lens.position.set(4.2, 16.0, 0);
      towerGroup.add(lens);

      // Subtle AI Optical Scanning Cone
      const coneGeo = new THREE.ConeGeometry(8, 22, 16, 1, true);
      const coneMat = new THREE.MeshBasicMaterial({
        color: 0x0F766E,
        transparent: true,
        opacity: 0.05,
        side: THREE.DoubleSide
      });
      const cone = new THREE.Mesh(coneGeo, coneMat);
      cone.rotation.z = -Math.PI / 3;
      cone.position.set(12, 6, 0);
      towerGroup.add(cone);
      scanningCones.push(cone);

      towerGroup.position.set(pos.x, pos.y, pos.z);
      towerGroup.rotation.y = pos.rot;
      scene.add(towerGroup);
      cctvTowers.push(towerGroup);
    });
  }

  /**
   * 3D Overhead Highway Gantry & Road Warning Signs
   */
  function createHighwayOverheadGantries() {
    const gantries = [
      { x: -35, y: 0, z: 25, rot: 0.35, text: "⚠ RHI SECTOR 4 - DEFECT AREA" },
      { x: 65, y: 0, z: 40, rot: -0.6, text: "CYBER HUB NORTH - 80 KM/H" }
    ];

    gantries.forEach(g => {
      const gantryGroup = new THREE.Group();
      const trussMat = new THREE.MeshStandardMaterial({ color: 0x94A3B8, metalness: 0.6, roughness: 0.4 });

      // Left Pillar
      const p1 = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.4, 14, 8), trussMat);
      p1.position.set(-6, 7, 0);
      gantryGroup.add(p1);

      // Right Pillar
      const p2 = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.4, 14, 8), trussMat);
      p2.position.set(6, 7, 0);
      gantryGroup.add(p2);

      // Overhead Cross Truss
      const truss = new THREE.Mesh(new THREE.BoxGeometry(13, 1.2, 1.2), trussMat);
      truss.position.set(0, 13.5, 0);
      gantryGroup.add(truss);

      // Electronic Matrix Sign Board (Navy Plate with Teal/Amber border)
      const signBoard = new THREE.Mesh(
        new THREE.BoxGeometry(9.5, 3.2, 0.4),
        new THREE.MeshStandardMaterial({ color: 0x0F172A, roughness: 0.2 })
      );
      signBoard.position.set(0, 13.5, 0.6);
      gantryGroup.add(signBoard);

      // Sign Inner Display Face
      const displayFace = new THREE.Mesh(
        new THREE.BoxGeometry(8.8, 2.6, 0.45),
        new THREE.MeshBasicMaterial({ color: 0x0F766E })
      );
      displayFace.position.set(0, 13.5, 0.65);
      gantryGroup.add(displayFace);

      gantryGroup.position.set(g.x, g.y, g.z);
      gantryGroup.rotation.y = g.rot;
      scene.add(gantryGroup);
    });
  }

  /**
   * High-Visibility Traffic Safety Cones & Construction Barrier Horses
   */
  function createTrafficSafetyCones() {
    const defectZones = [
      { x: -8, y: 6.5, z: 4 },
      { x: -12, y: 6.2, z: 7 },
      { x: -5, y: 6.6, z: 1 },
      { x: -65, y: 2.2, z: 42 },
      { x: -68, y: 2.2, z: 46 }
    ];

    defectZones.forEach(z => {
      const coneGroup = new THREE.Group();

      // Heavy Black Rubber Base
      const base = new THREE.Mesh(
        new THREE.BoxGeometry(1.6, 0.2, 1.6),
        new THREE.MeshStandardMaterial({ color: 0x1E293B })
      );
      coneGroup.add(base);

      // High-Vis Orange Cone
      const cone = new THREE.Mesh(
        new THREE.CylinderGeometry(0.15, 0.75, 2.4, 16),
        new THREE.MeshStandardMaterial({ color: 0xF59E0B, roughness: 0.4 })
      );
      cone.position.y = 1.2;
      coneGroup.add(cone);

      // Dual Reflective White Stripes
      const stripe1 = new THREE.Mesh(
        new THREE.CylinderGeometry(0.35, 0.5, 0.5, 16),
        new THREE.MeshBasicMaterial({ color: 0xFFFFFF })
      );
      stripe1.position.y = 1.0;
      coneGroup.add(stripe1);

      const stripe2 = new THREE.Mesh(
        new THREE.CylinderGeometry(0.2, 0.3, 0.35, 16),
        new THREE.MeshBasicMaterial({ color: 0xFFFFFF })
      );
      stripe2.position.y = 1.7;
      coneGroup.add(stripe2);

      coneGroup.position.set(z.x, z.y, z.z);
      scene.add(coneGroup);
    });

    // Construction Barrier Horses (Striped Safety Rail)
    const barrierLocs = [
      { x: -15, y: 6.8, z: 5, rot: 0.2 },
      { x: -72, y: 2.3, z: 44, rot: -0.4 }
    ];

    barrierLocs.forEach(b => {
      const barrierGroup = new THREE.Group();
      const legMat = new THREE.MeshStandardMaterial({ color: 0x94A3B8, metalness: 0.5 });
      const barMat = new THREE.MeshStandardMaterial({ color: 0xDC2626 }); // Striped Red

      // Support A-Frames
      const l1 = new THREE.Mesh(new THREE.BoxGeometry(0.2, 2.8, 1.8), legMat);
      l1.position.set(-2.5, 1.4, 0);
      const l2 = new THREE.Mesh(new THREE.BoxGeometry(0.2, 2.8, 1.8), legMat);
      l2.position.set(2.5, 1.4, 0);
      barrierGroup.add(l1);
      barrierGroup.add(l2);

      // Top Reflective Rail
      const rail = new THREE.Mesh(new THREE.BoxGeometry(5.4, 0.8, 0.2), barMat);
      rail.position.set(0, 2.2, 0);
      barrierGroup.add(rail);

      barrierGroup.position.set(b.x, b.y, b.z);
      barrierGroup.rotation.y = b.rot;
      scene.add(barrierGroup);
    });
  }

  /**
   * Animated 3D Floating GPS Teardrop Pins
   */
  function createGPSLocationPins() {
    const pins = [
      { x: 0, y: 15, z: 0, color: 0xDC2626, code: "DEF-1024", name: "Ring Road Sector 4" },
      { x: 80, y: 13, z: 35, color: 0x16A34A, code: "RHI-1042", name: "Cyber Hub North" },
      { x: -75, y: 12, z: -45, color: 0xF59E0B, code: "RHI-3091", name: "Metro Outer Bypass" }
    ];

    pins.forEach(p => {
      const pinGroup = new THREE.Group();

      // Top Sphere
      const head = new THREE.Mesh(
        new THREE.SphereGeometry(2.6, 16, 16),
        new THREE.MeshStandardMaterial({ color: p.color, roughness: 0.3, metalness: 0.3 })
      );
      head.position.y = 3.6;
      pinGroup.add(head);

      // Inner White Core
      const innerCore = new THREE.Mesh(
        new THREE.SphereGeometry(1.2, 12, 12),
        new THREE.MeshBasicMaterial({ color: 0xFFFFFF })
      );
      innerCore.position.y = 3.6;
      pinGroup.add(innerCore);

      // Inverted Pointing Cone
      const cone = new THREE.Mesh(
        new THREE.ConeGeometry(2.0, 4.4, 16),
        new THREE.MeshStandardMaterial({ color: p.color, roughness: 0.3 })
      );
      cone.rotation.x = Math.PI;
      cone.position.y = 1.4;
      pinGroup.add(cone);

      // Ground Target Ring
      const ringGeo = new THREE.RingGeometry(2.2, 2.8, 32);
      const ringMat = new THREE.MeshBasicMaterial({ color: p.color, transparent: true, opacity: 0.6, side: THREE.DoubleSide });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = -Math.PI / 2;
      ring.position.y = -p.y + 0.2;
      pinGroup.add(ring);

      pinGroup.position.set(p.x, p.y, p.z);
      scene.add(pinGroup);
      gpsPins.push({ group: pinGroup, ring: ring, baseY: p.y });
    });
  }

  /**
   * Roadside Landscaping Trees
   */
  function createRoadsideForestry() {
    const treeCoords = [
      [-85, 0, 45], [-65, 0, 75], [-40, 0, 90], [15, 0, 80], [50, 0, 60],
      [-105, 0, -40], [-40, 0, -45], [35, 0, -20], [70, 0, -55], [110, 0, 10],
      [-140, 0, 25], [125, 0, -45], [90, 0, -105], [-60, 0, -85],
      [5, 0, 110], [-25, 0, 130], [75, 0, 100], [-120, 0, 60]
    ];

    treeCoords.forEach(coord => {
      const tree = new THREE.Group();

      // Trunk
      const trunk = new THREE.Mesh(
        new THREE.CylinderGeometry(0.35, 0.5, 4.0, 6),
        new THREE.MeshStandardMaterial({ color: 0x78350F, roughness: 0.9 })
      );
      trunk.position.y = 2.0;
      tree.add(trunk);

      // Layered Emerald Foliage Cones
      const folMat = new THREE.MeshStandardMaterial({
        color: 0x16A34A, // Clean Emerald Green
        roughness: 0.85,
        flatShading: true
      });
      const c1 = new THREE.Mesh(new THREE.ConeGeometry(2.8, 3.8, 6), folMat);
      c1.position.y = 4.8;
      const c2 = new THREE.Mesh(new THREE.ConeGeometry(2.1, 3.2, 6), folMat);
      c2.position.y = 6.6;
      tree.add(c1);
      tree.add(c2);

      tree.position.set(coord[0], coord[1], coord[2]);
      const s = 0.9 + Math.random() * 0.45;
      tree.scale.set(s, s, s);
      scene.add(tree);
    });
  }

  function createTrafficFlowParticles() {
    roads.forEach((r) => {
      for (let i = 0; i < 3; i++) {
        const pMesh = new THREE.Mesh(
          new THREE.SphereGeometry(1.2, 8, 8),
          new THREE.MeshBasicMaterial({ color: i === 0 ? 0x0F766E : 0x2563EB })
        );
        scene.add(pMesh);

        trafficPoints.push({
          mesh: pMesh,
          curve: r.curve,
          progress: (i / 3) + Math.random() * 0.2,
          speed: 0.0014 + Math.random() * 0.0006
        });
      }
    });
  }

  function setCameraForHero() {
    currentViewMode = "hero";
    if (!camera) return;
    camera.position.set(0, 75, 190);
    camera.lookAt(0, 10, -15);
  }

  function setCameraForDashboard() {
    currentViewMode = "dashboard";
    if (!camera) return;
    // Rich isometric vantage angle over the entire road network
    camera.position.set(-50, 115, 150);
    camera.lookAt(5, 12, 0);
  }

  function switchView(mode) {
    currentViewMode = mode;
    if (mode === "dashboard") {
      if (dashContainer && renderer && renderer.domElement.parentElement !== dashContainer) {
        dashContainer.appendChild(renderer.domElement);
        onWindowResize();
      }
      setCameraForDashboard();
    } else {
      if (heroContainer && renderer && renderer.domElement.parentElement !== heroContainer) {
        heroContainer.appendChild(renderer.domElement);
        onWindowResize();
      }
      setCameraForHero();
    }
  }

  function onMouseMove(e) {
    mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
  }

  function onCanvasClick(e) {
    if (!renderer || e.target !== renderer.domElement) return;
    if (!raycaster || !camera) return;
    raycaster.setFromCamera(mouse, camera);
    const roadMeshes = roads.map(r => r.mesh);
    const intersects = raycaster.intersectObjects(roadMeshes);

    if (intersects.length > 0) {
      const hit = intersects[0].object;
      const data = hit.userData;
      console.log("[RHI 3D] Road Segment Clicked:", data);
      if (window.onRoadSegmentSelect) {
        window.onRoadSegmentSelect(data);
      }
    }
  }

  function onWindowResize() {
    if (!camera || !renderer) return;
    const container = currentViewMode === "dashboard" ? dashContainer : heroContainer;
    let w = container && container.clientWidth > 0 ? container.clientWidth : 0;
    let h = container && container.clientHeight > 0 ? container.clientHeight : 0;

    if (w === 0 || h === 0) {
      w = window.innerWidth || 800;
      h = window.innerHeight || 600;
    }

    if (w > 0 && h > 0) {
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    }
  }

  function animate() {
    animationFrameId = requestAnimationFrame(animate);

    // Guard: Only perform heavy 3D calculations and WebGL renders when container is visible
    const activeContainer = currentViewMode === "dashboard" ? dashContainer : heroContainer;
    const isVisible = activeContainer && activeContainer.offsetParent !== null && activeContainer.clientWidth > 0;

    if (!isVisible) {
      return;
    }

    clock += 0.022;

    // Smooth camera parallax from mouse position
    if (camera) {
      if (currentViewMode === "hero") {
        camera.position.x = mouse.x * 22;
        camera.position.y = 75 + mouse.y * 12;
        camera.lookAt(0, 10, -15);
      } else {
        camera.position.x = -50 + mouse.x * 16;
        camera.position.y = 115 + mouse.y * 10;
        camera.lookAt(5, 12, 0);
      }
    }

    // 1. Animate Traffic Flow Particles
    trafficPoints.forEach((tp) => {
      tp.progress += tp.speed;
      if (tp.progress > 1) tp.progress = 0;
      const pt = tp.curve.getPointAt(tp.progress);
      tp.mesh.position.set(pt.x, pt.y + 1.2, pt.z);
    });

    // 2. Animate Maintenance Patrol Trucks with realistic orientation
    maintenanceVehicles.forEach((mv) => {
      mv.progress += mv.speed;
      if (mv.progress > 0.99) mv.progress = 0.01;
      const pt = mv.curve.getPointAt(mv.progress);
      const tangent = mv.curve.getTangentAt(mv.progress);
      
      mv.group.position.set(pt.x, pt.y + 0.3, pt.z);
      mv.group.lookAt(pt.x + tangent.x, pt.y + 0.3 + tangent.y, pt.z + tangent.z);
    });

    // 3. Bob GPS Location Pins & Pulsing Ring Radii
    gpsPins.forEach((pin, i) => {
      pin.group.position.y = pin.baseY + Math.sin(clock * 2.2 + i) * 1.1;
      pin.group.rotation.y += 0.018;
      if (pin.ring) {
        const scale = 1 + Math.sin(clock * 3 + i) * 0.15;
        pin.ring.scale.set(scale, scale, 1);
      }
    });

    // 4. Oscillate CCTV Scanning Cones
    scanningCones.forEach((cone, i) => {
      cone.rotation.y = Math.sin(clock * 1.5 + i) * 0.35;
    });

    // 5. Render Scene
    if (renderer && scene && camera) {
      renderer.render(scene, camera);
    }
  }

  // ==========================================
  // MICRO 3D TELEMETRY WIDGETS
  // ==========================================

  let microVisualsInitialized = false;

  function initMicroVisuals() {
    if (microVisualsInitialized) return;
    microVisualsInitialized = true;
    initRadarWidget();
  }

  function initRadarWidget() {
    const canvas = document.getElementById("telemetry-lidar-canvas");
    if (!canvas || typeof THREE === "undefined") return;

    try {
      const w = canvas.clientWidth || 280;
      const h = canvas.clientHeight || 130;
      const rScene = new THREE.Scene();
      rScene.background = new THREE.Color(0x0F172A);

      const rCamera = new THREE.PerspectiveCamera(45, w / h, 0.1, 500);
      rCamera.position.set(0, 20, 32);
      rCamera.lookAt(0, 0, 0);

      const rRenderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
      rRenderer.setSize(w, h);
      rRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

      // Radar grid & concentric rings
      const polarGrid = new THREE.PolarGridHelper(16, 8, 4, 32, 0x0F766E, 0x1E293B);
      polarGrid.position.y = -0.5;
      rScene.add(polarGrid);

      // 3D wireframe road segment
      const roadGeo = new THREE.CylinderGeometry(12, 12, 1.2, 24, 2, true, 0, Math.PI);
      const roadMat = new THREE.MeshBasicMaterial({ color: 0x2DD4BF, wireframe: true, transparent: true, opacity: 0.6 });
      const roadMesh = new THREE.Mesh(roadGeo, roadMat);
      roadMesh.rotation.x = Math.PI / 2;
      rScene.add(roadMesh);

      // Sweeping radar beam line
      const beamGeo = new THREE.BufferGeometry();
      beamGeo.setAttribute("position", new THREE.Float32BufferAttribute([0, 0, 0, 0, 0, 16], 3));
      const beamMat = new THREE.LineBasicMaterial({ color: 0x38BDF8, linewidth: 2 });
      const beamLine = new THREE.Line(beamGeo, beamMat);
      rScene.add(beamLine);

      // Blip points
      const blipGeo = new THREE.BufferGeometry();
      const blipPos = [
        4, 0.2, 5,
        -6, 0.2, 8,
        8, 0.2, -4,
        -3, 0.2, -6
      ];
      blipGeo.setAttribute("position", new THREE.Float32BufferAttribute(blipPos, 3));
      const blipMat = new THREE.PointsMaterial({ color: 0xDC2626, size: 5, sizeAttenuation: false });
      const blips = new THREE.Points(blipGeo, blipMat);
      rScene.add(blips);

      let angle = 0;
      function renderRadar() {
        requestAnimationFrame(renderRadar);
        if (!canvas.offsetParent) return;
        angle += 0.035;
        beamLine.rotation.y = angle;
        roadMesh.rotation.z += 0.005;
        rRenderer.render(rScene, rCamera);
      }
      renderRadar();

      window.addEventListener("resize", () => {
        if (canvas.clientWidth && canvas.clientHeight) {
          rCamera.aspect = canvas.clientWidth / canvas.clientHeight;
          rCamera.updateProjectionMatrix();
          rRenderer.setSize(canvas.clientWidth, canvas.clientHeight);
        }
      });
    } catch (err) {
      console.warn("[RHI 3D] Radar visual notice:", err);
    }
  }

  return {
    init: init,
    switchView: switchView,
    setMode: switchView,
    setCameraForHero: setCameraForHero,
    setCameraForDashboard: setCameraForDashboard,
    resize: onWindowResize,
    initMicroVisuals: initMicroVisuals
  };
})();
