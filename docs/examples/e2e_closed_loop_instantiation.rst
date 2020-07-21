E2E Instantiation of a Closed Loop
##########################################


.. code:: Python

    #Service already created in this case

    logger = logging.getLogger("")
    logger.setLevel(logging.INFO)
    fh = logging.StreamHandler()
    fh_formatter = logging.Formatter('%(asctime)s %(levelname)s %(lineno)d:%(filename)s(%(process)d) - %(message)s')
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)


    #Constants
    SERVICE_NAME = "Test_SDK"
    POLICY_NAME = "MinMax"
    LOOP_INSTANCE_NAME = "instance01"
    OPERATIONAL_POLICY_NAME = "OPERATIONAL_" + SERVICE_NAME + POLICY_NAME


    Clamp.set_proxy({ 'http': 'socks5h://127.0.0.1:8080', 'https': 'socks5h://127.0.0.1:8080'})
    Service.set_proxy({ 'http': 'socks5h://127.0.0.1:8080', 'https': 'socks5h://127.0.0.1:8080'})

    logger.info("*******************************")
    logger.info("******** SERVICE FETCH *******")
    logger.info("*******************************")

    svc = Service(name=SERVICE_NAME)

    logger.info("***************************************")
    logger.info("******** CLAMP AUTHENTIFICATION *******")
    logger.info("***************************************")

    clamp = Clamp()
    Clamp.create_cert()

    logger.info("*************************************")
    logger.info("******** LOOP TEMPLATES CHECK *******")
    logger.info("*************************************")

    loop_template = Clamp.check_loop_template(service=svc)
    if not loop_template:
        logger.error("Loop template for the service %s not found", svc.name)
        exit(1)

    logger.info("*******************************")
    logger.info("******** POLICIES CHECK *******")
    logger.info("*******************************")

    policy_exists = Clamp.check_policies(policy_name=POLICY_NAME,
                                            req_policies=30)
    if not policy_exists:
        logger.error("Couldn't load the policy %s", POLICY_NAME)
        exit(1)

    logger.info("***********************************")
    logger.info("******** LOOP INSTANTIATION *******")
    logger.info("***********************************")

    loop = LoopInstance(template=loop_template, name=LOOP_INSTANCE_NAME, details={})
    details = loop.create()
    if details:
        logger.info("Loop instance %s successfully created !!", LOOP_INSTANCE_NAME)
    else:
        logger.error("An error occured while creating the loop instance")

    logger.info("******** UPDATE MICROSERVICE POLICY *******")
    loop._update_loop_details()
    loop.update_microservice_policy()

    #add works well but the configuration isn't working
    logger.info("******** ADD OPERATIONAL POLICY *******")
    added = loop.add_operational_policy(policy_type="onap.policies.controlloop.guard.common.MinMax",
                                        policy_version="1.0.0")

    logger.info("******** CONFIGURE OPERATIONAL POLICY *******")
    loop.add_op_policy_config(loop.add_minmax_config, name=OPERATIONAL_POLICY_NAME)

    logger.info("******** ADD OPERATIONAL POLICY *******")
    added = loop.add_operational_policy(policy_type="onap.policies.controlloop.guard.common.MinMax",
                                        policy_version="1.0.0")

    logger.info("******** CONFIGURE OPERATIONAL POLICY *******")
    loop.add_op_policy_config(loop.add_minmax_config, name=OPERATIONAL_POLICY_NAME)

    logger.info("******** SUBMIT POLICIES TO PE *******")
    submit = loop.act_on_loop_policy(action="submit")

    logger.info("******** CHECK POLICIES SUBMITION *******")
    if submit :
        logger.info("Policies successfully submited to PE")
    else:
        logger.error("An error occured while submitting the loop instance")
        exit(1)
    """
    #deploy not working in  clamp UI
    logger.info("******** DEPLOY LOOP INSTANCE *******")
    deploy = loop.deploy_microservice_to_dcae()
    if submit:
        logger.info("Loop instance %s successfully deployed on DCAE !!", LOOP_INSTANCE_NAME)
    else:
        logger.error("An error occured while deploying the loop instance")
        exit(2)

    #works well
    logger.info("******** DELETE LOOP INSTANCE *******")
    loop.delete()
    #An error will occur related to CLAMP problems but the loop still is deleted
    """
