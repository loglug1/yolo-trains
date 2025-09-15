export class Video {
    constructor(title,video_id){
        this.title = title;
        this.video_id = video_id
    }
}

export class Model {
    constructor(model_title, model_id) {
        this.model_title = model_title;
        this.model_id = model_id;
    }
}

export class Frame {
    constructor(frame_num, objects){
        this.frame_num = frame_num;
        this.objects = objects;
    }
}

export class DetectionObject {
    constructor(object_type, x1, x2, y1, y2, confidence) {
        this.object_type = object_type;
        this.x1 = x1;
        this.x2 = x2;
        this.y1 = y1;
        this.y2 = y2;
        this.confidence = confidence;
    }
}