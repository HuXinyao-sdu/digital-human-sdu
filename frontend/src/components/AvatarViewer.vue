<template>
  <div ref="container" class="avatar-viewer" role="img" aria-label="校史数字人模型">
    <p v-if="status === 'loading'" class="viewer-message">数字人模型加载中…</p>
    <p v-else-if="status === 'error'" class="viewer-message viewer-error">
      {{ errorMessage }}
    </p>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm'

const emit = defineEmits(['loaded', 'error'])

const container = ref(null)
const status = ref('loading')
const errorMessage = ref('')

let renderer
let scene
let camera
let vrm
let frameId
let resizeObserver
let clock
let leftUpperArm
let rightUpperArm
let chest
let head
let idleStartTime = 0
let audioContext
let analyser
let audioData
let audioSource
let connectedAudioElement
let lipSyncActive = false

const visemeCandidates = [
  ['aa', 'a', 'A'],
  ['ih', 'i', 'I'],
  ['ou', 'u', 'U'],
  ['ee', 'e', 'E'],
  ['oh', 'o', 'O'],
]
let visemeNames = []

const setNaturalPose = () => {
  // 根据每条手臂的实际骨骼方向计算向下的站立姿势，避免依赖模型的局部坐标轴。
  leftUpperArm = vrm.humanoid?.getNormalizedBoneNode('leftUpperArm')
  rightUpperArm = vrm.humanoid?.getNormalizedBoneNode('rightUpperArm')
  chest = vrm.humanoid?.getNormalizedBoneNode('chest')
  head = vrm.humanoid?.getNormalizedBoneNode('head')

  const lowerArmNaturally = (upperArm, lowerArm) => {
    if (!upperArm || !lowerArm) return

    scene.updateMatrixWorld(true)
    const upperPosition = upperArm.getWorldPosition(new THREE.Vector3())
    const lowerPosition = lowerArm.getWorldPosition(new THREE.Vector3())
    const currentDirection = lowerPosition.sub(upperPosition).normalize()
    const downwardDirection = new THREE.Vector3(0, -1, 0)
    const worldRotation = new THREE.Quaternion().setFromUnitVectors(
      currentDirection,
      downwardDirection
    )
    const currentWorldQuaternion = upperArm.getWorldQuaternion(new THREE.Quaternion())
    const desiredWorldQuaternion = worldRotation.multiply(currentWorldQuaternion)
    const parentWorldQuaternion = upperArm.parent?.getWorldQuaternion(new THREE.Quaternion())

    if (parentWorldQuaternion) {
      upperArm.quaternion.copy(parentWorldQuaternion.invert().multiply(desiredWorldQuaternion))
    }
  }

  lowerArmNaturally(
    leftUpperArm,
    vrm.humanoid?.getNormalizedBoneNode('leftLowerArm')
  )
  lowerArmNaturally(
    rightUpperArm,
    vrm.humanoid?.getNormalizedBoneNode('rightLowerArm')
  )
}

const updateIdleMotion = () => {
  if (!vrm) return

  const elapsed = clock.elapsedTime - idleStartTime
  const breath = Math.sin(elapsed * 1.7)

  // 极轻微的呼吸与视线变化，避免数字人在待机时完全静止。
  if (chest) chest.rotation.x = breath * 0.012
  if (head) {
    head.rotation.y = Math.sin(elapsed * 0.55) * 0.025
    head.rotation.x = breath * 0.008
  }

  const blinkPhase = elapsed % 4.6
  const blink = blinkPhase < 0.12 ? Math.sin((blinkPhase / 0.12) * Math.PI) : 0
  vrm.expressionManager?.setValue('blink', blink)
}

const updateLipSync = () => {
  if (!analyser || !vrm?.expressionManager || !lipSyncActive) return

  analyser.getByteTimeDomainData(audioData)
  const average = audioData.reduce((sum, value) => sum + Math.abs(value - 128), 0) / audioData.length
  const mouthOpen = Math.min(1, Math.max(0, (average - 2) / 18))
  const activeIndex = Math.floor(clock.elapsedTime * 10) % visemeNames.length

  visemeNames.forEach((name, index) => {
    vrm.expressionManager.setValue(name, index === activeIndex ? mouthOpen : 0)
  })
}

const resetVisemes = () => {
  visemeNames.forEach((name) => vrm?.expressionManager?.setValue(name, 0))
}

const startLipSync = async (audioElement) => {
  if (!audioElement || !vrm?.expressionManager) return

  if (!audioContext) {
    audioContext = new AudioContext()
    analyser = audioContext.createAnalyser()
    analyser.fftSize = 256
    audioData = new Uint8Array(analyser.fftSize)
    analyser.connect(audioContext.destination)
  }

  // 每轮问答都会产生新的 Audio 实例；每个实例各自绑定一次分析节点。
  if (connectedAudioElement !== audioElement) {
    audioSource?.disconnect()
    audioSource = audioContext.createMediaElementSource(audioElement)
    audioSource.connect(analyser)
    connectedAudioElement = audioElement
  }

  if (audioContext.state === 'suspended') await audioContext.resume()
  lipSyncActive = true
}

const stopLipSync = () => {
  lipSyncActive = false
  resetVisemes()
}

const render = () => {
  const delta = clock.getDelta()
  updateIdleMotion()
  updateLipSync()
  vrm?.update(delta)
  renderer.render(scene, camera)
  frameId = requestAnimationFrame(render)
}

const resize = () => {
  if (!container.value || !renderer || !camera) return

  const { clientWidth: width, clientHeight: height } = container.value
  if (!width || !height) return

  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height, false)
}

const disposeObject = (object) => {
  object.traverse((child) => {
    if (!child.isMesh) return
    child.geometry?.dispose()
    const materials = Array.isArray(child.material) ? child.material : [child.material]
    materials.filter(Boolean).forEach((material) => material.dispose())
  })
}

onMounted(() => {
  scene = new THREE.Scene()
  scene.background = new THREE.Color('#241d20')

  camera = new THREE.PerspectiveCamera(28, 1, 0.1, 100)
  camera.position.set(0, 1.62, 2.05)
  camera.lookAt(0, 1.48, 0)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.shadowMap.enabled = true
  container.value.appendChild(renderer.domElement)

  scene.add(new THREE.HemisphereLight(0xfff5e5, 0x28232b, 2.4))

  const keyLight = new THREE.DirectionalLight(0xffe8d2, 2.6)
  keyLight.position.set(1.5, 3, 2)
  keyLight.castShadow = true
  scene.add(keyLight)

  const fillLight = new THREE.DirectionalLight(0xc9dcff, 1.2)
  fillLight.position.set(-2, 1.5, 1)
  scene.add(fillLight)

  const rimLight = new THREE.DirectionalLight(0xd49b7c, 1.4)
  rimLight.position.set(0, 2, -2)
  scene.add(rimLight)

  clock = new THREE.Clock()
  resizeObserver = new ResizeObserver(resize)
  resizeObserver.observe(container.value)
  resize()

  const loader = new GLTFLoader()
  loader.register((parser) => new VRMLoaderPlugin(parser))
  loader.load(
    '/models/avatar.vrm',
    (gltf) => {
      vrm = gltf.userData.vrm
      if (!vrm) {
        const error = new Error('文件中没有可用的 VRM 数据。')
        console.error(error)
        errorMessage.value = '数字人模型格式无效，请确认它是 VRM 文件。'
        status.value = 'error'
        emit('error', error)
        return
      }

      // 本地模型为 VRM 0.x；转换坐标以匹配 three.js 的正面朝向。
      VRMUtils.rotateVRM0(vrm)
      vrm.scene.scale.setScalar(2.15)
      vrm.scene.position.set(0, -1.02, 0)
      scene.add(vrm.scene)
      setNaturalPose()
      visemeNames = visemeCandidates
        .map((candidates) => candidates.find((name) => vrm.expressionManager?.getExpression(name)))
        .filter(Boolean)
      idleStartTime = clock.elapsedTime
      status.value = 'ready'
      emit('loaded')
    },
    undefined,
    (error) => {
      console.error('VRM model load error:', error)
      errorMessage.value = '数字人模型加载失败，请确认本地 avatar.vrm 文件存在。'
      status.value = 'error'
      emit('error', error)
    }
  )

  render()
})

onBeforeUnmount(() => {
  cancelAnimationFrame(frameId)
  resizeObserver?.disconnect()
  stopLipSync()
  audioSource?.disconnect()
  audioContext?.close()
  if (vrm?.scene) disposeObject(vrm.scene)
  renderer?.dispose()
  renderer?.domElement.remove()
})

defineExpose({ startLipSync, stopLipSync })
</script>

<style scoped>
.avatar-viewer {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: inherit;
}

.avatar-viewer :deep(canvas) {
  display: block;
  width: 100%;
  height: 100%;
}

.viewer-message {
  position: absolute;
  inset: 0;
  z-index: 1;
  display: grid;
  place-items: center;
  margin: 0;
  padding: 24px;
  color: #ded8d0;
  font-size: 14px;
  text-align: center;
}

.viewer-error { color: #ffb4a8; }
</style>
