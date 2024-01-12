package it.netfarm.mymedbook.mymedtag.api;

import java.lang.annotation.ElementType;
import java.lang.annotation.Target;


@Target(ElementType.FIELD)
public @interface SkipSerialisation {

}
