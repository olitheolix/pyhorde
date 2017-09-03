cimport pyhorde
from types import SimpleNamespace

# Expose Horde3D constants.
h3dRootNode = H3DRootNode
h3dRenderDevice = SimpleNamespace(OpenGL2=OpenGL2, OpenGL4=OpenGL4)
h3dModelUpdateFlags = SimpleNamespace(Animation=Animation, Geometry=Geometry)
h3dOptions = SimpleNamespace(
    MaxLogLevel=MaxLogLevel,
    MaxNumMessages=MaxNumMessages,
    TrilinearFiltering=TrilinearFiltering,
    MaxAnisotropy=MaxAnisotropy,
    TexCompression=TexCompression,
    SRGBLinearization=SRGBLinearization,
    LoadTextures=LoadTextures,
    FastAnimation=FastAnimation,
    ShadowMapSize=ShadowMapSize,
    SampleCount=SampleCount,
    WireframeMode=WireframeMode,
    DebugViewMode=DebugViewMode,
    DumpFailedShaders=DumpFailedShaders,
    GatherTimeStat=GatherTimeStats
)
h3dResTypes = SimpleNamespace(
    Undefined=Undefined,
    SceneGraph=SceneGraph,
    Geometry=Geometry,
    Animation=Animation,
    Material=Material,
    Code=Code,
    Shader=Shader,
    Texture=Texture,
    ParticleEffect=ParticleEffect,
    Pipeline=Pipeline,
)
h3dNodeTypes = SimpleNamespace(
    Undefined=Undefined,
    Group=Group,
    Model=Model,
    Mesh=Mesh,
    Joint=Joint,
    Light=Light,
    Camera=Camera,
    Emitter=Emitter,
)
h3dNodeFlags = SimpleNamespace(
    NoDraw=NoDraw,
    NoCastShadow=NoCastShadow,
    NoRayQuery=NoRayQuery,
    Inactive=Inactive,
)
h3dLight = SimpleNamespace(
    MatRes=MatRes,
    RadiusF=RadiusF,
    FovF=FovF,
    ColorF3=ColorF3,
    ColorMultiplierF=ColorMultiplierF,
    ShadowMapCountI=ShadowMapCountI,
    ShadowSplitLambdaF=ShadowSplitLambdaF,
    ShadowMapBiasF=ShadowMapBiasF,
    LightingContextStr=LightingContextStr,
    ShadowContextStr=ShadowContextStr,
)
h3dCamera = SimpleNamespace(
    PipeResI=PipeResI,
    OutTexResI=OutTexResI,
    OutBufIndexI=OutBufIndexI,
    LeftPlaneF=LeftPlaneF,
    RightPlaneF=RightPlaneF,
    BottomPlaneF=BottomPlaneF,
    TopPlaneF=TopPlaneF,
    NearPlaneF=NearPlaneF,
    FarPlaneF=FarPlaneF,
    ViewportXI=ViewportXI,
    ViewportYI=ViewportYI,
    ViewportWidthI=ViewportWidthI,
    ViewportHeightI=ViewportHeightI,
    OrthoI=OrthoI,
    OccCullingI=OccCullingI,
)
h3dPartEffRes = SimpleNamespace(
    ParticleElem=ParticleElem,
    ChanMoveVelElem=ChanMoveVelElem,
    ChanRotVelElem=ChanRotVelElem,
    ChanSizeElem=ChanSizeElem,
    ChanColRElem=ChanColRElem,
    ChanColGElem=ChanColGElem,
    ChanColBElem=ChanColBElem,
    ChanColAElem=ChanColAElem,
    PartLifeMinF=PartLifeMinF,
    PartLifeMaxF=PartLifeMaxF,
    ChanStartMinF=ChanStartMinF,
    ChanStartMaxF=ChanStartMaxF,
    ChanEndRateF=ChanEndRateF,
    ChanDragElem=ChanDragElem,
)
h3dEmitter = SimpleNamespace(
    MatResI=MatResI,
    PartEffResI=PartEffResI,
    MaxCountI=MaxCountI,
    RespawnCountI=RespawnCountI,
    DelayF=DelayF,
    EmissionRateF=EmissionRateF,
    SpreadAngleF=SpreadAngleF,
    ForceF3=ForceF3,
)


cpdef createEGLContext(int width, int height):
    cdef EGLDisplay eglDpy = initEGL(width, height)
    cdef unsigned long c_handle = <unsigned long>eglDpy
    assert eglDpy != NULL
    return int(c_handle)


cpdef releaseEGLContext(unsigned long ctx):
    cdef EGLDisplay eglDpy = <EGLDisplay>ctx
    releaseEGL(eglDpy)


cdef class Engine:
    def __init__(self, width=512, height=512, int GLVersion=2):
        # Initialise Horde engine with selected OpenGL version.
        if GLVersion == 2:
            assert h3dInit(OpenGL2) is True
        elif GLVersion == 4:
            assert h3dInit(OpenGL4) is True
        else:
            print('OpenGL version must be either 2 or 4')
            assert False

    def __dealloc__(self):
        h3dRelease()

    def shutdown(self):
        h3dRelease()

    def h3dScreenshotFile(self, str fname):
        cdef string c_fname = fname.encode('utf8')
        return h3dutScreenshot(c_fname.c_str())

    def h3dSetOption(self, ListH3DOptions param, float value):
        return h3dSetOption(param, value)

    def h3dAddResource(self, int rtype, str name, int flags):
        cdef string s = name.encode('utf8')
        return h3dAddResource(rtype, s.c_str(), flags)

    def h3dAddNode(self, H3DNode parent, H3DRes sceneGraphRes):
        return h3dAddNodes(parent, sceneGraphRes)

    def h3dRemoveNode(self, H3DNode node):
        h3dRemoveNode(node)

    def h3dAddCameraNode(self, H3DNode parent, str name, H3DRes pipelineRes):
        cdef string s = name.encode('utf8')
        return h3dAddCameraNode(parent, s.c_str(), pipelineRes)

    def h3dSetNodeTransform(self, H3DNode node, float tx, float ty, float tz,
                         float rx, float ry, float rz, float sx, float sy,
                         float sz):
        return h3dSetNodeTransform(node, tx, ty, tz, rx, ry, rz, sx, sy, sz)

    def h3dSetNodeTransMat(self, H3DNode node, float[:] mat44):
        return h3dSetNodeTransMat(node, &mat44[0])

    def h3dGetNodeTransform(self, H3DNode node):
        cdef float v[9];
        h3dGetNodeTransform(
            node, &(v[0]), &v[1], &v[2], &v[3], &v[4], &v[5], &v[6], &v[7], &v[8])
        return [float(v[_]) for _ in range(9)]

    def h3dGetNodeTransMat(self, H3DNode node):
        # Horde does not copy the TM into an array of our choosing, but gives
        # us a pointer to its the internal data structure.
        cdef const float *ptr
        h3dGetNodeTransMats(node, &ptr, NULL)
        return <unsigned char[:16 * sizeof(float)]><unsigned char*>(&(ptr[0]))

    def h3dAddLightNode(self, H3DNode parent,
                     str name,
                     H3DRes materialRes,
                     str lightingContext,
                     str shadowContext):
        cdef string cname = name.encode('utf8')
        cdef string clc = lightingContext.encode('utf8')
        cdef string csc = shadowContext.encode('utf8')

        return h3dAddLightNode(parent, cname.c_str(),
                               materialRes, clc.c_str(), csc.c_str())

    def h3dSetNodeParamI(self, H3DNode node, int param, int value):
        return h3dSetNodeParamI(node, param, value)

    def h3dSetNodeParamF(self, H3DNode node, int param, int compIdx, float value):
        return h3dSetNodeParamF(node, param, compIdx, value)

    def h3dGetNodeParamI(self, H3DNode node, int param):
        return h3dGetNodeParamI(node, param)

    def h3dGetNodeParamF(self, H3DNode node, int param, int compIdx):
        return h3dGetNodeParamF(node, param, compIdx)

    def h3dClearOverlays(self):
        return h3dClearOverlays()

    def h3dFinalizeFrame(self):
        return h3dFinalizeFrame()

    def h3dRender(self, H3DNode cameraNode):
        return h3dRender(cameraNode)

    def h3dResizePipelineBuffers(self, H3DRes pipeRes, int width, int height):
        return h3dResizePipelineBuffers(pipeRes, width, height)

    def h3dSetupCameraView(self, H3DNode cameraNode, float fov, float aspect,
                        float nearDist, float farDist):
        return h3dSetupCameraView(cameraNode, fov, aspect,
                        nearDist, farDist)

    def h3dUtLoadResourcesFromDisk(self, str contentDir):
        cdef string ccd = contentDir.encode('utf8')
        return h3dutLoadResourcesFromDisk(ccd.c_str())

    def h3dUtDumpMessages(self):
        return h3dutDumpMessages()

    def h3dScreenshotDimensions(self):
        cdef int width, height;
        h3dutGetScreenshotParam(&width, &height)
        return width, height

    def h3dScreenshot(self, unsigned char[:] ui8buf):
        cdef int width, height;
        h3dutGetScreenshotParam(&width, &height)
        assert len(ui8buf) == width * height * 3
        return h3dutScreenshotRaw(&ui8buf[0], len(ui8buf))

    def h3dCloneResource(self, H3DRes res, str name):
        cdef string c_name = name.encode('utf8')
        h3dCloneResource(res, c_name.c_str())

    def h3dSetResParamI(self, H3DRes res, int elem, int elemIdx, int param, int value):
        h3dSetResParamI(res, elem, elemIdx, param, value)

    def h3dLoadResource(self, H3DRes res, bytes data):
        return h3dLoadResource(res, data, len(data))

    def h3dFindResource(self, int rtype, str name):
        tmp = name.encode('utf8')
        cdef char *c_name = tmp
        return h3dFindResource(rtype, c_name)

    def h3dGetNextResource(self, rtype, H3DRes start):
        return h3dGetNextResource(rtype, start)

    def h3dFindNodes(self, H3DNode startNode, str name, int rtype):
        tmp = name.encode('utf8')
        cdef char *c_name = tmp
        return h3dFindNodes(startNode, c_name, rtype)

    def h3dGetNodeFindResult(self, int index):
        return h3dGetNodeFindResult(index)

    def h3dGetNodeChild(self, H3DNode node, int index):
        return h3dGetNodeChild(node, index)

    def h3dGetNodeParent(self, H3DNode node):
        return h3dGetNodeParent(node)

    def h3dSetNodeParent(self, H3DNode node, H3DNode parent) -> bool:
        return h3dSetNodeParent(node, parent)

    def h3dGetNodeType(self, H3DNode node):
        return h3dGetNodeType(node)

    def h3dSetNodeFlags(self, H3DNode node, int flags, bint recursive):
        h3dSetNodeFlags(node, flags, recursive)

    def h3dCheckNodeVisibility(self, H3DNode node, H3DNode camera):
        return h3dCheckNodeVisibility(node, camera, True, False)

    def h3dSetMaterialUniform(self, H3DRes res, str name,
                              float a, float b, float c, float d):
        tmp = name.encode('utf8')
        cdef char *c_name = tmp
        h3dSetMaterialUniform(res, c_name, a, b, c, d)

    def h3dAddEmitterNode(self, H3DNode parent, str name, H3DRes materialRes,
                          H3DRes particleEffectRes, int maxParticleCount,
                          int respawnCount):
        tmp = name.encode('utf8')
        cdef char *c_name = tmp
        return h3dAddEmitterNode(
            parent, c_name, materialRes, particleEffectRes,
            maxParticleCount, respawnCount)

    def h3dUpdateEmitter(self, H3DNode emitterNode, float timeDelta):
        h3dUpdateEmitter(emitterNode, timeDelta)

    def h3dHasEmitterFinished(self, H3DNode emitterNode):
        return h3dHasEmitterFinished(emitterNode)

    def h3dUpdateModel(self, H3DNode modelNode, int flags):
        h3dUpdateModel(modelNode, flags)

    def h3dSetupModelAnimStage(self, H3DNode modelNode, int stage, H3DRes animationRes,
                               int layer, str startNode, bint additive):
        tmp = startNode.encode('utf8')
        cdef char *c_startNode = tmp
        return h3dSetupModelAnimStage(
            modelNode, stage, animationRes, layer, c_startNode, additive)

    def h3dGetNodeAABB(self, H3DNode node):
        cdef float x0, y0, z0, x1, y1, z1
        h3dGetNodeAABB(node, &x0, &y0, &z0, &x1, &y1, &z1)
        return (x0, y0, z0, x1, y1, z1)
